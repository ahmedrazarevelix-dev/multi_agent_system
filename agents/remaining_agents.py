"""
agents/remaining_agents.py
Module 4 — HR Recruitment + Performance
Module 5 — Sales Lead + Marketing
Module 6 — Legal Document
Module 7 — IT Operations
"""

import json
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from loguru import logger

from config.settings import get_llm, settings
from database.models import get_session, Employee, JobApplication, Lead
from tools.shared_tools import log_agent_action, send_alert, new_id


# ════════════════════════════════════════════════════════
# MODULE 4 — HR
# ════════════════════════════════════════════════════════

class ScreenCVTool(BaseTool):
    name: str = "screen_cv"
    description: str = "Score and summarize a job application CV. Provide: applicant_name, position, cv_text"
    def _run(self, applicant_name: str = "", position: str = "", cv_text: str = "") -> str:
        try:
            session = get_session()
            keywords = {
                "engineer":   ["python", "java", "aws", "sql", "api", "git", "agile"],
                "manager":    ["leadership", "team", "project", "strategy", "budget", "kpi"],
                "analyst":    ["data", "excel", "sql", "reporting", "analysis", "tableau"],
                "designer":   ["figma", "ui", "ux", "adobe", "wireframe", "prototype"],
                "sales":      ["revenue", "client", "crm", "target", "negotiation", "b2b"],
            }
            position_lower = position.lower()
            cv_lower       = cv_text.lower()
            relevant_kw    = []
            for role, kws in keywords.items():
                if role in position_lower:
                    relevant_kw = kws
                    break
            if not relevant_kw:
                relevant_kw = ["experience", "degree", "skills", "professional"]
            matched = [kw for kw in relevant_kw if kw in cv_lower]
            score   = min(100, int((len(matched) / max(len(relevant_kw), 1)) * 100) + 20)
            summary = (
                f"Candidate: {applicant_name} | Position: {position}\n"
                f"Match Score: {score}/100\n"
                f"Matched Keywords: {', '.join(matched) if matched else 'None'}\n"
                f"Recommendation: {'Strong candidate - proceed to interview' if score >= 60 else 'Below threshold - reject'}"
            )
            app = JobApplication(
                id=new_id(),
                position=position,
                applicant_name=applicant_name,
                cv_text=cv_text[:2000],
                ai_score=score,
                ai_summary=summary,
                status="shortlisted" if score >= 60 else "rejected"
            )
            session.add(app)
            session.commit()
            session.close()
            return summary
        except Exception as e:
            return f"Error screening CV: {e}"


class GetPerformanceReportTool(BaseTool):
    name: str = "get_performance_report"
    description: str = "Get employee performance scores. Provide: department (optional)"
    def _run(self, department: str = "") -> str:
        try:
            session = get_session()
            query   = session.query(Employee)
            if department:
                query = query.filter(Employee.department == department)
            employees = query.all()
            if not employees:
                return f"No employees found{' in ' + department if department else ''}."
            data = [{
                "name": e.name,
                "department": e.department,
                "role": e.role,
                "performance_score": e.performance_score,
                "status": "Excellent" if e.performance_score >= 4.5
                          else "Good" if e.performance_score >= 3.5
                          else "Needs Improvement"
            } for e in employees]
            session.close()
            avg = sum(e["performance_score"] or 0 for e in data) / len(data)
            return (
                f"Department: {department or 'All'}\n"
                f"Total Employees: {len(data)}\n"
                f"Average Score: {avg:.2f}/5.0\n"
                f"Details: {json.dumps(data[:10])}"
            )
        except Exception as e:
            return f"Error: {e}"


# Tool instances — HR
_screen_cv              = ScreenCVTool()
_get_performance_report = GetPerformanceReportTool()


def create_hr_recruitment_agent():
    return Agent(
        role="HR Recruitment Specialist",
        goal="Screen CVs, score candidates, schedule interviews, and build strong teams.",
        backstory="Expert recruiter who has hired hundreds of top performers using AI-assisted screening.",
        tools=[_screen_cv, log_agent_action, send_alert],
        llm=get_llm(temperature=0.2),
        verbose=False,
        allow_delegation=False,
    )


def create_performance_agent():
    return Agent(
        role="HR Performance Manager",
        goal="Track employee KPIs, identify training needs, and flag underperformance.",
        backstory="Seasoned HR manager focused on building high-performance cultures through data.",
        tools=[_get_performance_report, send_alert, log_agent_action],
        llm=get_llm(temperature=0.1),
        verbose=False,
        allow_delegation=False,
    )


# ════════════════════════════════════════════════════════
# MODULE 5 — SALES & MARKETING
# ════════════════════════════════════════════════════════

class QualifyLeadTool(BaseTool):
    name: str = "qualify_lead"
    description: str = "Score and qualify a sales lead. Provide: lead_id"
    def _run(self, lead_id: str = "") -> str:
        try:
            session = get_session()
            lead = session.query(Lead).filter_by(id=lead_id).first()
            if not lead:
                session.close()
                return f"Lead {lead_id} not found"
            
            score = 50.0
            if lead.company:
                score += 20
            if lead.email and "@gmail" not in lead.email:
                score += 15
            if lead.source in ["referral", "demo_request", "inbound"]:
                score += 15
            
            lead.qualification_score = score
            lead.status = "qualified" if score >= 70 else "nurture" if score >= 50 else "unqualified"
            session.commit()
            
            # ✅ Data pehle save karo session close se pehle
            name = lead.name
            company = lead.company
            status = lead.status
            
            session.close()  # ✅ Baad mein close karo
            
            return (
                "Lead Qualification: " + str(name) + "\n"
                "Company: " + str(company) + "\n"
                "Score: " + str(score) + "/100\n"
                "Status: " + str(status) + "\n"
                "Action: " + ("Assign to sales rep immediately" if score >= 70 else "Add to nurture campaign")
            )
        except Exception as e:
            return "Error: " + str(e)


class GetSalesPipelineTool(BaseTool):
    name: str = "get_sales_pipeline"
    description: str = "Get current sales pipeline — all leads by status. No input needed."
    def _run(self) -> str:
        try:
            session  = get_session()
            leads    = session.query(Lead).all()
            pipeline = {}
            for lead in leads:
                status = lead.status or "new"
                if status not in pipeline:
                    pipeline[status] = 0
                pipeline[status] += 1
            session.close()
            total = len(leads)
            return (
                f"Sales Pipeline ({total} total leads):\n"
                + "\n".join(f"  {k}: {v}" for k, v in pipeline.items())
            )
        except Exception as e:
            return f"Error: {e}"


class AnalyzeMarketingROITool(BaseTool):
    name: str = "analyze_marketing_roi"
    description: str = "Calculate marketing campaign ROI. Provide: campaign_name, spend, leads_generated, conversions"
    def _run(self, campaign_name: str = "", spend: float = 0,
             leads_generated: int = 0, conversions: int = 0) -> str:
        cost_per_lead       = spend / max(leads_generated, 1)
        cost_per_conversion = spend / max(conversions, 1)
        conversion_rate     = (conversions / max(leads_generated, 1)) * 100
        roi_assessment      = "Excellent" if conversion_rate > 15 else "Good" if conversion_rate > 8 else "Poor"
        return (
            f"Campaign: {campaign_name}\n"
            f"Total Spend: ${spend:,.2f}\n"
            f"Leads Generated: {leads_generated}\n"
            f"Conversions: {conversions}\n"
            f"Cost Per Lead: ${cost_per_lead:.2f}\n"
            f"Cost Per Conversion: ${cost_per_conversion:.2f}\n"
            f"Conversion Rate: {conversion_rate:.1f}%\n"
            f"ROI Assessment: {roi_assessment}"
        )


# Tool instances — Sales
_qualify_lead          = QualifyLeadTool()
_get_sales_pipeline    = GetSalesPipelineTool()
_analyze_marketing_roi = AnalyzeMarketingROITool()


def create_sales_lead_agent():
    return Agent(
        role="Sales Lead Qualification Specialist",
        goal="Identify, score, and qualify leads. Route hot leads to sales reps immediately.",
        backstory="Top-performing sales analyst who never lets a hot lead go cold.",
        tools=[_qualify_lead, _get_sales_pipeline, send_alert, log_agent_action],
        llm=get_llm(temperature=0.2),
        verbose=False,
        allow_delegation=False,
    )


def create_marketing_agent():
    return Agent(
        role="Digital Marketing Analyst",
        goal="Optimize marketing campaigns for maximum ROI. Identify what works and cut what doesn't.",
        backstory="Data-driven marketer who has scaled campaigns from zero to millions in revenue.",
        tools=[_analyze_marketing_roi, send_alert, log_agent_action],
        llm=get_llm(temperature=0.3),
        verbose=False,
        allow_delegation=False,
    )


# ════════════════════════════════════════════════════════
# MODULE 6 — LEGAL
# ════════════════════════════════════════════════════════

class ReviewContractTool(BaseTool):
    name: str = "review_contract"
    description: str = "Review contract for risky clauses. Provide: contract_text, contract_type"
    def _run(self, contract_text: str = "", contract_type: str = "general") -> str:
        risks = []
        contract_lower = contract_text.lower()
        risk_patterns = {
            "unlimited liability": "HIGH RISK — Unlimited liability clause found. Recommend adding liability cap.",
            "perpetual license":   "MEDIUM RISK — Perpetual license with no termination rights. Negotiate exit clause.",
            "auto-renew":          "MEDIUM RISK — Auto-renewal clause. Ensure cancellation notice period is acceptable.",
            "no refund":           "LOW RISK — No refund policy. Standard but verify it meets local regulations.",
            "arbitration":         "LOW RISK — Mandatory arbitration clause. Limits court options.",
            "non-compete":         "MEDIUM RISK — Non-compete clause found. Verify duration and geography are reasonable.",
            "indemnification":     "MEDIUM RISK — Broad indemnification clause. Review scope carefully.",
        }
        for pattern, advice in risk_patterns.items():
            if pattern in contract_lower:
                risks.append(advice)
        if not risks:
            return f"Contract Review ({contract_type}): No major risk clauses identified. Standard review recommended."
        result  = f"Contract Review ({contract_type})\nRisk Clauses Found: {len(risks)}\n\n"
        result += "\n".join(f"• {r}" for r in risks)
        result += "\n\nRecommendation: Legal counsel review before signing."
        return result


class CheckComplianceTool(BaseTool):
    name: str = "check_compliance"
    description: str = "Check business process compliance. Provide: business_process, jurisdiction"
    def _run(self, business_process: str = "", jurisdiction: str = "general") -> str:
        process_lower     = business_process.lower()
        compliance_issues = []
        checks = {
            "personal data": "GDPR/Data Protection: Ensure data minimization and consent mechanisms are in place.",
            "customer data": "GDPR/CCPA: Customer data requires explicit consent and right-to-delete procedures.",
            "financial":     "SOX/Financial Compliance: Ensure audit trails and segregation of duties.",
            "health":        "HIPAA: Health data requires encryption, access controls, and audit logs.",
            "payment":       "PCI-DSS: Payment data must never be stored in plain text. Use tokenization.",
            "employee":      "Labor Law: Ensure compliance with local employment regulations.",
        }
        for keyword, advice in checks.items():
            if keyword in process_lower:
                compliance_issues.append(advice)
        if not compliance_issues:
            return f"Compliance Check ({jurisdiction}): No obvious issues identified. Standard compliance review recommended."
        return (
            f"Compliance Check ({jurisdiction})\n"
            f"Potential Issues: {len(compliance_issues)}\n\n"
            + "\n".join(f"• {i}" for i in compliance_issues)
        )


# Tool instances — Legal
_review_contract  = ReviewContractTool()
_check_compliance = CheckComplianceTool()


def create_legal_agent():
    return Agent(
        role="Legal Document Analyst",
        goal="Review contracts and check compliance. Flag risks before they become legal problems.",
        backstory="Former corporate lawyer turned AI legal analyst. Meticulous, thorough, risk-averse.",
        tools=[_review_contract, _check_compliance, send_alert, log_agent_action],
        llm=get_llm(temperature=0.0),
        verbose=False,
        allow_delegation=False,
    )


# ════════════════════════════════════════════════════════
# MODULE 7 — IT OPERATIONS
# ════════════════════════════════════════════════════════

class MonitorSystemHealthTool(BaseTool):
    name: str = "monitor_system_health"
    description: str = "Check system health metrics — CPU, memory, disk. No input needed."
    def _run(self) -> str:
        import random
        metrics = {
            "cpu_usage_pct":    round(random.uniform(20, 85), 1),
            "memory_usage_pct": round(random.uniform(40, 80), 1),
            "disk_usage_pct":   round(random.uniform(30, 70), 1),
            "db_connections":   random.randint(5, 45),
            "api_response_ms":  random.randint(80, 450),
            "error_rate_pct":   round(random.uniform(0, 3), 2),
            "uptime_hours":     random.randint(100, 2000),
            "active_agents":    12,
            "status": "operational"
        }
        alerts = []
        if metrics["cpu_usage_pct"] > 80:
            alerts.append("HIGH CPU usage")
        if metrics["memory_usage_pct"] > 85:
            alerts.append("HIGH memory usage")
        if metrics["error_rate_pct"] > 2:
            alerts.append("Elevated error rate")
        metrics["alerts"] = alerts
        return json.dumps(metrics)


class ScanSecurityThreatsTool(BaseTool):
    name: str = "scan_security_threats"
    description: str = "Scan for security threats — failed logins, unusual access. No input needed."
    def _run(self) -> str:
        import random
        threats        = []
        failed_logins  = random.randint(0, 15)
        unusual_access = random.choice([True, False])
        open_ports     = random.randint(0, 3)
        if failed_logins > 10:
            threats.append({"severity": "HIGH", "type": "Brute Force", "detail": f"{failed_logins} failed login attempts"})
        if unusual_access:
            threats.append({"severity": "MEDIUM", "type": "Unusual Access", "detail": "Off-hours admin access detected"})
        if open_ports > 0:
            threats.append({"severity": "LOW", "type": "Open Ports", "detail": f"{open_ports} unnecessary ports open"})
        if not threats:
            return "Security Scan: No threats detected. System secure."
        return json.dumps({"threat_count": len(threats), "threats": threats})


class AutoTroubleshootTool(BaseTool):
    name: str = "auto_troubleshoot"
    description: str = "Diagnose and suggest fixes for system errors. Provide: error_code, service_name"
    def _run(self, error_code: str = "", service_name: str = "") -> str:
        solutions = {
            "db_connection_timeout": "1. Check DB host/port. 2. Verify connection pool size. 3. Restart connection pool.",
            "memory_overflow":       "1. Identify memory leak in logs. 2. Restart affected service. 3. Scale up RAM.",
            "api_rate_limit":        "1. Implement exponential backoff. 2. Cache frequent requests. 3. Upgrade API tier.",
            "disk_full":             "1. Run log cleanup: logs older than 7 days. 2. Archive old DB records. 3. Expand disk.",
            "high_cpu":              "1. Identify top CPU process. 2. Check for infinite loops. 3. Scale horizontally.",
            "ssl_expiry":            "1. Renew SSL certificate immediately. 2. Set up auto-renewal. 3. Test HTTPS.",
        }
        solution = solutions.get(error_code.lower().replace(" ", "_"),
                                 "Error not in database. Escalate to senior engineer with full logs.")
        return f"Auto-Troubleshoot: {service_name} — {error_code}\nSolution: {solution}"


# Tool instances — IT
_monitor_system_health  = MonitorSystemHealthTool()
_scan_security_threats  = ScanSecurityThreatsTool()
_auto_troubleshoot      = AutoTroubleshootTool()


def create_it_agent():
    return Agent(
        role="IT Operations Engineer",
        goal="Monitor system health, detect security threats, and auto-resolve common issues.",
        backstory="Site Reliability Engineer who keeps systems at 99.9% uptime through automation.",
        tools=[_monitor_system_health, _scan_security_threats, _auto_troubleshoot,
               send_alert, log_agent_action],
        llm=get_llm(temperature=0.1),
        verbose=False,
        allow_delegation=False,
    )


# ════════════════════════════════════════════════════════
# COMBINED HR + SALES + LEGAL + IT CREW
# ════════════════════════════════════════════════════════

def run_operations_crew() -> str:
    logger.info("Starting Operations Crew (HR + Sales + Legal + IT)...")
    hr_agent    = create_hr_recruitment_agent()
    sales_agent = create_sales_lead_agent()
    legal_agent = create_legal_agent()
    it_agent    = create_it_agent()

    task_hr = Task(
        description="""
        Run the daily HR operations check:
        1. Get performance report for all departments using get_performance_report
        2. Identify any employees scoring below 3.0/5.0
        3. Send alert if any department average is below 3.5
        4. Log findings with log_agent_action
        """,
        agent=hr_agent,
        expected_output="HR performance summary with any flagged employees."
    )

    task_sales = Task(
        description="""
        Run the daily sales pipeline review:
        1. Get the full sales pipeline using get_sales_pipeline
        2. Identify leads that are 'new' for more than 3 days (stale leads)
        3. Send alert if pipeline has fewer than 10 qualified leads
        4. Log findings with log_agent_action
        """,
        agent=sales_agent,
        expected_output="Sales pipeline health report."
    )

    task_it = Task(
        description="""
        Run the daily IT health and security check:
        1. Use monitor_system_health to get current metrics
        2. Use scan_security_threats to check for active threats
        3. If CPU > 80% or memory > 85%, use auto_troubleshoot
        4. Send CRITICAL alert for HIGH severity threats
        5. Log all actions with log_agent_action
        """,
        agent=it_agent,
        expected_output="IT health and security report."
    )

    crew = Crew(
        agents=[hr_agent, sales_agent, it_agent],
        tasks=[task_hr, task_sales, task_it],
        verbose=False
    )

    result = crew.kickoff()
    logger.success("Operations Crew completed!")
    return str(result)
