"""
agents/finance_agents.py
Module 3 — Financial Analysis Agent + Fraud Detection Agent
"""

import json
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from loguru import logger

from config.settings import get_llm, settings
from database.models import get_session, Transaction, FinancialReport, RiskLevel
from tools.shared_tools import log_agent_action, send_alert, new_id


# ─────────────────────────────────────────────
# TOOLS — Finance  
# ─────────────────────────────────────────────

class GetFinancialSummaryTool(BaseTool):
    name: str = "get_financial_summary"
    description: str = "Get financial summary for the last N days. Provide: period_days"
    def _run(self, period_days: int = 30) -> str:
        try:
            session = get_session()
            since = datetime.utcnow() - timedelta(days=period_days)
            transactions = session.query(Transaction).filter(
                Transaction.created_at >= since
            ).all()
            total_revenue  = sum(t.amount for t in transactions if t.type == "sale")
            total_expenses = sum(t.amount for t in transactions if t.type == "expense")
            total_refunds  = sum(t.amount for t in transactions if t.type == "refund")
            net_profit     = total_revenue - total_expenses - total_refunds
            flagged_count  = sum(1 for t in transactions if t.is_flagged)
            session.close()
            return json.dumps({
                "period_days": period_days,
                "total_transactions": len(transactions),
                "total_revenue": round(total_revenue, 2),
                "total_expenses": round(total_expenses, 2),
                "total_refunds": round(total_refunds, 2),
                "net_profit": round(net_profit, 2),
                "profit_margin": f"{(net_profit/max(total_revenue,1))*100:.1f}%",
                "flagged_transactions": flagged_count,
                "period_start": str(since.date()),
                "period_end": str(datetime.utcnow().date())
            })
        except Exception as e:
            return f"Error: {e}"


class GenerateFinancialReportTool(BaseTool):
    name: str = "generate_financial_report"
    description: str = "Generate and save financial report. Provide: period_days, report_type"
    def _run(self, period_days: int = 30, report_type: str = "monthly") -> str:
        try:
            session = get_session()
            since   = datetime.utcnow() - timedelta(days=period_days)
            txns    = session.query(Transaction).filter(Transaction.created_at >= since).all()
            revenue  = sum(t.amount for t in txns if t.type == "sale")
            expenses = sum(t.amount for t in txns if t.type == "expense")
            profit   = revenue - expenses
            margin   = (profit / max(revenue, 1)) * 100
            report = FinancialReport(
                id=new_id(),
                report_type=report_type,
                period_start=since,
                period_end=datetime.utcnow(),
                total_revenue=round(revenue, 2),
                total_expenses=round(expenses, 2),
                net_profit=round(profit, 2),
                report_data={
                    "transaction_count": len(txns),
                    "profit_margin": round(margin, 2),
                    "avg_transaction": round(revenue / max(len(txns), 1), 2)
                },
                ai_insights=f"Profit margin of {margin:.1f}%. {'Healthy' if margin > 20 else 'Needs improvement'}."
            )
            session.add(report)
            session.commit()
            report_id = report.id
            session.close()
            return (
                f"Financial Report {report_id} generated!\n"
                f"Period: Last {period_days} days\n"
                f"Revenue: ${revenue:,.2f}\n"
                f"Expenses: ${expenses:,.2f}\n"
                f"Net Profit: ${profit:,.2f}\n"
                f"Margin: {margin:.1f}%\n"
                f"Status: {'Profitable' if profit > 0 else 'Loss-making'}"
            )
        except Exception as e:
            return f"Error generating report: {e}"

    
class GetCashflowTrendTool(BaseTool):
    name: str = "get_cashflow_trend"
    description: str = "Get daily cash flow trend for last N days. Provide: days"
    def _run(self, days: int = 7) -> str:
        try:
            session = get_session()
            daily_data = {}
            for d in range(days):
                day     = datetime.utcnow() - timedelta(days=d)
                day_str = day.strftime("%Y-%m-%d")
                txns    = session.query(Transaction).filter(
                    Transaction.created_at >= day.replace(hour=0, minute=0, second=0),
                    Transaction.created_at <  day.replace(hour=23, minute=59, second=59)
                ).all()
                inflow  = sum(t.amount for t in txns if t.type == "sale")
                outflow = sum(t.amount for t in txns if t.type in ["expense", "refund"])
                daily_data[day_str] = {
                    "inflow": round(inflow, 2),
                    "outflow": round(outflow, 2),
                    "net": round(inflow - outflow, 2)
                }
            session.close()
            return json.dumps(daily_data)
        except Exception as e:
            return f"Error: {e}"


# ─────────────────────────────────────────────
# TOOLS — Fraud Detection
# ─────────────────────────────────────────────

class ScanForFraudTool(BaseTool):
    name: str = "scan_for_fraud"
    description: str = "Scan recent transactions for fraud. Provide: hours_back"
    def _run(self, hours_back: int = 24) -> str:
        try:
            session  = get_session()
            since    = datetime.utcnow() - timedelta(hours=hours_back)
            txns     = session.query(Transaction).filter(
                Transaction.created_at >= since,
                Transaction.is_flagged == False
            ).all()
            flagged   = []
            threshold = settings.FRAUD_AMOUNT_THRESHOLD
            velocity  = settings.FRAUD_VELOCITY_THRESHOLD
            customer_txns: dict = {}
            for t in txns:
                if t.customer_id not in customer_txns:
                    customer_txns[t.customer_id] = []
                customer_txns[t.customer_id].append(t)
            for t in txns:
                reasons     = []
                fraud_score = 0.0
                if t.amount > threshold:
                    reasons.append(f"High amount: ${t.amount:,.0f}")
                    fraud_score += 0.5
                cust_count = len(customer_txns.get(t.customer_id, []))
                if cust_count > velocity:
                    reasons.append(f"High velocity: {cust_count} transactions")
                    fraud_score += 0.4
                if 2 <= t.created_at.hour <= 5:
                    reasons.append("Unusual hour transaction")
                    fraud_score += 0.2
                if reasons:
                    fraud_score = min(fraud_score, 1.0)
                    risk = (
                        RiskLevel.CRITICAL if fraud_score >= 0.8
                        else RiskLevel.HIGH if fraud_score >= 0.6
                        else RiskLevel.MEDIUM
                    )
                    t.is_flagged  = True
                    t.fraud_score = fraud_score
                    t.risk_level  = risk
                    flagged.append({
                        "transaction_id": t.id,
                        "customer_id": t.customer_id,
                        "amount": t.amount,
                        "fraud_score": round(fraud_score, 2),
                        "risk_level": risk.value,
                        "reasons": reasons
                    })
            session.commit()
            session.close()
            if not flagged:
                return f"No suspicious transactions found in last {hours_back} hours."
            return json.dumps({"flagged_count": len(flagged), "transactions": flagged})
        except Exception as e:
            return f"Error scanning: {e}"


class FreezeTransactionTool(BaseTool):
    name: str = "freeze_transaction"
    description: str = "Freeze a suspicious transaction. Provide: transaction_id, reason"
    def _run(self, transaction_id: str = "", reason: str = "") -> str:
        try:
            session = get_session()
            txn     = session.query(Transaction).filter_by(id=transaction_id).first()
            if not txn:
                return f"Transaction {transaction_id} not found"
            txn.is_flagged = True
            txn.status     = "frozen"
            session.commit()
            session.close()
            return f"Transaction {transaction_id} frozen. Reason: {reason}"
        except Exception as e:
            return f"Error: {e}"


class GetCustomerRiskProfileTool(BaseTool):
    name: str = "get_customer_risk_profile"
    description: str = "Get risk profile for a customer. Provide: customer_id"
    def _run(self, customer_id: str = "") -> str:
        try:
            session = get_session()
            txns    = session.query(Transaction).filter_by(customer_id=customer_id).all()
            if not txns:
                return f"No transaction history found for customer {customer_id}"
            total_amount  = sum(t.amount for t in txns)
            avg_amount    = total_amount / len(txns)
            flagged_count = sum(1 for t in txns if t.is_flagged)
            flag_rate     = flagged_count / len(txns)
            risk = "HIGH" if flag_rate > 0.3 else "MEDIUM" if flag_rate > 0.1 else "LOW"
            session.close()
            return (
                f"Customer Risk Profile: {customer_id}\n"
                f"Total Transactions: {len(txns)}\n"
                f"Average Amount: ${avg_amount:,.2f}\n"
                f"Flagged Transactions: {flagged_count} ({flag_rate:.0%})\n"
                f"Overall Risk: {risk}"
            )
        except Exception as e:
            return f"Error: {e}"


# Tool instances
_get_financial_summary     = GetFinancialSummaryTool()
_generate_financial_report = GenerateFinancialReportTool()
_get_cashflow_trend        = GetCashflowTrendTool()
_scan_for_fraud            = ScanForFraudTool()
_freeze_transaction        = FreezeTransactionTool()
_get_customer_risk_profile = GetCustomerRiskProfileTool()


# ─────────────────────────────────────────────
# AGENT 5 — Financial Analysis Agent
# ─────────────────────────────────────────────

def create_finance_agent():
    llm = get_llm(temperature=0.1)
    return Agent(
        role="Senior Financial Analyst",
        goal=(
            "Monitor financial health of the business in real-time. "
            "Generate reports, track cash flow, identify trends, "
            "and flag financial anomalies before they become problems."
        ),
        backstory=(
            "You are a CPA-level financial analyst with expertise in business intelligence. "
            "You transform raw transaction data into actionable insights, "
            "and you always highlight the most critical financial metrics first."
        ),
        tools=[_get_financial_summary, _generate_financial_report, _get_cashflow_trend,
               send_alert, log_agent_action],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


# ─────────────────────────────────────────────
# AGENT 6 — Fraud Detection Agent
# ─────────────────────────────────────────────

def create_fraud_agent():
    llm = get_llm(temperature=0.0)
    return Agent(
        role="Financial Fraud Detection Specialist",
        goal=(
            "Detect and prevent financial fraud in real-time. "
            "Scan transactions for suspicious patterns, freeze risky transactions, "
            "and alert the security team immediately."
        ),
        backstory=(
            "You are a former financial crimes investigator with deep expertise in fraud patterns. "
            "You never let a suspicious transaction pass undetected. "
            "You are thorough, methodical, and always err on the side of caution."
        ),
        tools=[_scan_for_fraud, _freeze_transaction, _get_customer_risk_profile,
               send_alert, log_agent_action],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


# ─────────────────────────────────────────────
# CREW — Finance & Fraud Module
# ─────────────────────────────────────────────

def run_finance_crew() -> str:
    logger.info("Starting Finance & Fraud Detection Crew...")
    finance_agent = create_finance_agent()
    fraud_agent   = create_fraud_agent()
    task1 = Task(
        description="""
        Perform a comprehensive fraud scan:
        1. Use scan_for_fraud to check the last 24 hours of transactions
        2. For any flagged transactions, get the customer risk profile
        3. Freeze any CRITICAL risk transactions using freeze_transaction
        4. Send a CRITICAL alert if fraud score > 0.8
        5. Send a WARNING alert if flagged_count > 5
        6. Log all findings with log_agent_action
        Be thorough — financial fraud causes major business damage.
        """,
        agent=fraud_agent,
        expected_output="Fraud scan report with flagged transactions and actions taken."
    )
    task2 = Task(
        description="""
        Generate a comprehensive financial health report:
        1. Use get_financial_summary for the last 30 days
        2. Use get_cashflow_trend for the last 7 days
        3. Use generate_financial_report to save the report to database
        4. Identify any concerning trends (declining revenue, high expenses)
        5. Send a WARNING alert if profit margin < 10%
        6. Log all actions with log_agent_action
        Provide actionable insights, not just numbers.
        """,
        agent=finance_agent,
        expected_output="Complete financial health report with insights and recommendations.",
        context=[task1]
    )
    crew = Crew(
        agents=[fraud_agent, finance_agent],
        tasks=[task1, task2],
        verbose=False
    )
    result = crew.kickoff()
    logger.success("Finance & Fraud Crew completed!")
    return str(result)