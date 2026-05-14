"""
agents/master_orchestrator.py
Fixed — pure BaseTool, no @tool decorator, no StructuredTool
"""
 
import time
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from loguru import logger
 
from config.settings import get_llm, settings
from tools.shared_tools import log_agent_action, send_alert
 
from agents.customer_service_agents import run_customer_service_crew
from agents.inventory_agents import run_inventory_crew
from agents.finance_agents import run_finance_crew
from agents.remaining_agents import run_operations_crew
 
 
# ─────────────────────────────────────────────
# ALL TOOLS — pure BaseTool (no @tool decorator)
# ─────────────────────────────────────────────
 
class ClassifyProblemTool(BaseTool):
    name: str = "classify_business_problem"
    description: str = "Classify what type of business problem this is. Provide: problem_description"
 
    def _run(self, problem_description: str = "") -> str:
        problem_lower = problem_description.lower()
        classifications = {
            "customer_service": ["complaint","angry","support","ticket","refund","unhappy","customer","service","order"],
            "inventory":        ["stock","inventory","out of stock","supply","reorder","warehouse","shortage","supplier"],
            "finance":          ["revenue","profit","loss","expense","budget","financial","transaction","fraud","suspicious","payment"],
            "hr":               ["employee","hire","recruit","cv","performance","salary","human resource","interview","staff"],
            "sales":            ["lead","prospect","deal","pipeline","conversion","crm","sale","marketing","campaign"],
            "it":               ["system down","error","bug","server","security","breach","crash","infrastructure","health","threat"],
            "legal":            ["contract","legal","compliance","regulation","lawsuit","agreement","gdpr","audit"],
            "full_scan":        ["daily scan","full scan","all modules","complete check","run everything","scan all"],
        }
        scores = {}
        for dept, keywords in classifications.items():
            score = sum(1 for kw in keywords if kw in problem_lower)
            if score > 0:
                scores[dept] = score
 
        if not scores:
            return "GENERAL | No specific department. Run full system check."
 
        best = max(scores, key=scores.get)
        confidence = min(100, scores[best] * 25)
        return f"{best.upper()} | Confidence: {confidence}% | Route to: {best} crew"
 
 
class RouteCustomerComplaintTool(BaseTool):
    name: str = "route_customer_complaint"
    description: str = "Route a customer complaint to Customer Service crew. Provide: customer_id, complaint"
 
    def _run(self, customer_id: str = "CUST-001", complaint: str = "") -> str:
        logger.info(f"Routing to Customer Service Crew: {customer_id}")
        try:
            return run_customer_service_crew(customer_id, complaint)
        except Exception as e:
            return f"Customer service crew error: {e}"
 
 
class RunInventoryCheckTool(BaseTool):
    name: str = "run_inventory_check"
    description: str = "Trigger full inventory health check and supply chain optimization. No input needed."
 
    def _run(self) -> str:
        logger.info("Routing to Inventory & Supply Chain Crew...")
        try:
            return run_inventory_crew()
        except Exception as e:
            return f"Inventory crew error: {e}"
 
 
class RunFinanceCheckTool(BaseTool):
    name: str = "run_finance_check"
    description: str = "Trigger financial analysis and fraud detection scan. No input needed."
 
    def _run(self) -> str:
        logger.info("Routing to Finance & Fraud Crew...")
        try:
            return run_finance_crew()
        except Exception as e:
            return f"Finance crew error: {e}"
 
 
class RunOperationsCheckTool(BaseTool):
    name: str = "run_operations_check"
    description: str = "Trigger HR, Sales, Legal, and IT operations checks. No input needed."
 
    def _run(self) -> str:
        logger.info("Routing to Operations Crew...")
        try:
            return run_operations_crew()
        except Exception as e:
            return f"Operations crew error: {e}"
 
 
class RunFullDailyScanTool(BaseTool):
    name: str = "run_full_daily_scan"
    description: str = "Run complete daily scan across ALL modules — finance, inventory, operations. No input needed."
 
    def _run(self) -> str:
        logger.info("Starting FULL daily system scan...")
        results = []
        try:
            logger.info("1/3 Finance & Fraud...")
            run_finance_crew()
            results.append("Finance & Fraud: Done")
        except Exception as e:
            results.append(f"Finance: Error — {e}")
 
        try:
            logger.info("2/3 Inventory & Supply Chain...")
            run_inventory_crew()
            results.append("Inventory & Supply Chain: Done")
        except Exception as e:
            results.append(f"Inventory: Error — {e}")
 
        try:
            logger.info("3/3 Operations (HR + Sales + IT)...")
            run_operations_crew()
            results.append("Operations (HR/Sales/IT): Done")
        except Exception as e:
            results.append(f"Operations: Error — {e}")
 
        return (
            "FULL DAILY SCAN COMPLETE\n"
            "========================\n"
            + "\n".join(results)
            + "\nAll reports saved. Check logs/alerts.log for alerts."
        )
 
 
# ─────────────────────────────────────────────
# TOOL INSTANCES
# ─────────────────────────────────────────────
 
classify_tool    = ClassifyProblemTool()
customer_tool    = RouteCustomerComplaintTool()
inventory_tool   = RunInventoryCheckTool()
finance_tool     = RunFinanceCheckTool()
operations_tool  = RunOperationsCheckTool()
daily_scan_tool  = RunFullDailyScanTool()
 
 
# ─────────────────────────────────────────────
# MASTER ORCHESTRATOR AGENT
# ─────────────────────────────────────────────
 
def create_master_orchestrator():
    llm = get_llm(temperature=0.1)
    return Agent(
        role="Master Business AI Orchestrator",
        goal=(
            "Understand any incoming business problem. "
            "Classify it correctly. Route it to the right specialized crew. "
            "Coordinate all 12 agents to solve complex multi-department problems."
        ),
        backstory=(
            "You are the central intelligence of a multi-agent business system. "
            "You have supervised Customer Service, Finance, HR, Sales, Supply Chain, Legal, and IT. "
            "You always classify first, then route to the correct crew."
        ),
        tools=[
            classify_tool,
            customer_tool,
            inventory_tool,
            finance_tool,
            operations_tool,
            daily_scan_tool,
            send_alert,
            log_agent_action,
        ],
        llm=llm,
        verbose=True,
        max_iter=settings.MAX_ITERATIONS,
        allow_delegation=False,
    )
 
 
# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
 
def process_business_request(request: str, context: dict = None) -> str:
    start_time = time.time()
    logger.info(f"New business request received: {request[:100]}...")
 
    orchestrator = create_master_orchestrator()
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
 
    task = Task(
        description=f"""
        Business Request: "{request}"
        {f'Additional Context: {context}' if context else ''}
        Current Time: {current_time}
 
        Your job:
        1. Use classify_business_problem tool to identify the department
        2. Route to the correct crew tool based on classification:
           - customer_service → route_customer_complaint
           - inventory → run_inventory_check
           - finance → run_finance_check
           - hr/sales/it/legal → run_operations_check
           - full_scan → run_full_daily_scan
        3. Return a clear executive summary of what was done
 
        Always classify first, then route. Be decisive.
        """,
        agent=orchestrator,
        expected_output="Executive summary: classification, crew activated, actions taken, outcome."
    )
 
    crew = Crew(
        agents=[orchestrator],
        tasks=[task],
        verbose=True
    )
 
    result   = crew.kickoff()
    duration = round((time.time() - start_time) * 1000)
    logger.success(f"Request processed in {duration}ms")
    return str(result)
 
 
# ─────────────────────────────────────────────
# PLAN TRACKING (in-memory)
# ─────────────────────────────────────────────
 
_plans = {}
 
 
def get_plan(plan_id: str):
    return _plans.get(plan_id)
 
 
def get_all_plans():
    return list(_plans.values())
 
 
# ─────────────────────────────────────────────
# DAILY SCHEDULE
# ─────────────────────────────────────────────
 
def run_daily_schedule():
    logger.info("=== DAILY SCHEDULED RUN STARTED ===")
    result = process_business_request("Run complete daily scan for all business modules")
    logger.info("=== DAILY SCHEDULED RUN COMPLETE ===")
    return result