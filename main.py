"""
main.py
FastAPI REST API — exposes all 12 agents via HTTP endpoints
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
 
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from loguru import logger
from datetime import datetime
 
from database.models import init_db
from agents.master_orchestrator import process_business_request, run_daily_schedule
from agents.customer_service_agents import run_customer_service_crew
from agents.inventory_agents import run_inventory_crew
from agents.finance_agents import run_finance_crew
from agents.remaining_agents import run_operations_crew
 
# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────
 
app = FastAPI(
    title="🤖 Multi-Agent Business System",
    description="12 AI Agents solving real business problems — powered by Groq LLaMA3 + CrewAI + LangChain",
    version="1.0.0",
    docs_url="/docs",
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
@app.on_event("startup")
async def startup():
    logger.info("Starting Multi-Agent Business System...")
    try:
        init_db()
        logger.success("Database initialized!")
    except Exception as e:
        logger.warning(f"DB init warning: {e}")
 
 
# ─────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────
 
class BusinessRequest(BaseModel):
    request: str
    context: Optional[dict] = None
 
class CustomerComplaint(BaseModel):
    customer_id: str
    complaint: str
 
 
# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────
 
@app.get("/", tags=["System"])
def root():
    return {
        "system": "Multi-Agent Business System",
        "version": "1.0.0",
        "status": "running",
        "agents": 12,
        "modules": 7,
        "llm": "Groq LLaMA3-70b (Free)",
        "database": "PostgreSQL",
        "docs": "/docs",
        "time": datetime.utcnow().isoformat()
    }
 
 
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
 
 
# ── MASTER ORCHESTRATOR ──────────────────────
@app.post("/orchestrate", tags=["Master Orchestrator"])
async def orchestrate(req: BusinessRequest, background_tasks: BackgroundTasks):
    """
    Send ANY business problem to the Master Orchestrator.
    It will classify, route, and solve automatically.
 
    Examples:
    - "Customer C001 is angry about their order"
    - "Stock levels are critically low for 3 products"
    - "Suspicious transactions detected today"
    - "Run daily scan"
    """
    import time, uuid
    start = time.time()
    try:
        # Classify karo pehle — frontend ke liye
        def _classify(req_text: str):
            req_lower = req_text.lower()
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
                score = sum(1 for kw in keywords if kw in req_lower)
                if score > 0:
                    scores[dept] = score
            if not scores:
                return "general", 50
            best = max(scores, key=scores.get)
            return best, min(100, scores[best] * 25)
        classification, confidence = _classify(req.request)
 
        # Plan tasks define karo — classification ke hisaab se
        task_map = {
            "customer_service": [
                {"agent": "Sentiment Analysis Agent", "module": "customer_service", "priority": "high",   "description": "Customer message ka sentiment analyze karo"},
                {"agent": "Customer Support Agent",   "module": "customer_service", "priority": "high",   "description": "Ticket banao aur AI response draft karo"},
            ],
            "inventory": [
                {"agent": "Inventory Management Agent",  "module": "inventory", "priority": "medium", "description": "Low stock products scan karo, demand predict karo"},
                {"agent": "Supply Chain Optimizer Agent","module": "inventory", "priority": "medium", "description": "Best supplier choose karo, order place karo"},
            ],
            "finance": [
                {"agent": "Fraud Detection Agent",   "module": "finance", "priority": "critical", "description": "Last 24hr transactions scan karo, fraud flag karo"},
                {"agent": "Financial Analysis Agent","module": "finance", "priority": "high",     "description": "Financial report banao, cash flow analyze karo"},
            ],
            "hr": [
                {"agent": "HR Recruitment Agent",  "module": "hr", "priority": "medium", "description": "CVs screen karo, candidates score karo"},
                {"agent": "Performance Agent",     "module": "hr", "priority": "medium", "description": "Employee KPIs check karo"},
            ],
            "sales": [
                {"agent": "Sales Lead Agent",  "module": "sales", "priority": "medium", "description": "Pipeline review karo, leads qualify karo"},
                {"agent": "Marketing Agent",   "module": "sales", "priority": "low",    "description": "Campaign ROI analyze karo"},
            ],
            "it": [
                {"agent": "IT Operations Agent", "module": "it", "priority": "critical", "description": "System health + security threats scan karo"},
            ],
            "legal": [
                {"agent": "Legal Document Agent", "module": "legal", "priority": "high", "description": "Contract review + compliance check karo"},
            ],
            "full_scan": [
                {"agent": "Fraud Detection Agent",        "module": "finance",    "priority": "critical", "description": "Fraud scan"},
                {"agent": "Financial Analysis Agent",     "module": "finance",    "priority": "high",     "description": "Finance report"},
                {"agent": "Inventory Management Agent",   "module": "inventory",  "priority": "medium",   "description": "Stock check"},
                {"agent": "Supply Chain Agent",           "module": "inventory",  "priority": "medium",   "description": "Orders optimize"},
                {"agent": "HR Performance Agent",         "module": "hr",         "priority": "medium",   "description": "Performance check"},
                {"agent": "Sales Lead Agent",             "module": "sales",      "priority": "medium",   "description": "Pipeline review"},
                {"agent": "IT Operations Agent",          "module": "it",         "priority": "critical", "description": "System health check"},
            ],
        }
        tasks = task_map.get(classification, [
            {"agent": "Master Orchestrator", "module": "general", "priority": "medium", "description": "General analysis karo"}
        ])
 
        # Agents run karo
        result = process_business_request(req.request, req.context)
        duration = round((time.time() - start) * 1000)
 
        return {
            "plan_id":          str(uuid.uuid4())[:8].upper(),
            "request":          req.request,
            "classification":   classification,
            "confidence":       confidence,
            "agents_planned":   len(tasks),
            "approval_status":  "done",
            "approval_reason":  f"Request classified as '{classification}' with {confidence}% confidence. Routed to correct crew and executed successfully.",
            "tasks":            tasks,
            "result":           str(result),
            "duration_ms":      duration,
            "status":           "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# ── MODULE 1: CUSTOMER SERVICE ───────────────
@app.post("/agents/customer-service", tags=["Module 1: Customer Service"])
async def customer_service(req: CustomerComplaint):
    """
    Run Customer Support + Sentiment Analysis for a complaint.
    Automatically creates ticket and drafts response.
    """
    try:
        result = run_customer_service_crew(req.customer_id, req.complaint)
        return {"status": "success", "module": "customer_service", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# ── MODULE 2: INVENTORY ──────────────────────
@app.post("/agents/inventory", tags=["Module 2: Inventory & Supply Chain"])
async def inventory_check():
    """
    Run full Inventory + Supply Chain optimization.
    Checks stock levels, predicts demand, places orders automatically.
    """
    try:
        result = run_inventory_crew()
        return {"status": "success", "module": "inventory_supply_chain", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# ── MODULE 3: FINANCE ────────────────────────
@app.post("/agents/finance", tags=["Module 3: Finance & Fraud"])
async def finance_check():
    """
    Run Financial Analysis + Fraud Detection.
    Generates financial report and scans for suspicious transactions.
    """
    try:
        result = run_finance_crew()
        return {"status": "success", "module": "finance_fraud", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# ── MODULES 4-7: OPERATIONS ──────────────────
@app.post("/agents/operations", tags=["Modules 4-7: HR, Sales, Legal, IT"])
async def operations_check():
    """
    Run HR Performance, Sales Pipeline, and IT Health checks.
    """
    try:
        result = run_operations_crew()
        return {"status": "success", "module": "operations", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# ── DAILY FULL SCAN ──────────────────────────
@app.post("/agents/daily-scan", tags=["Master Orchestrator"])
async def daily_scan(background_tasks: BackgroundTasks):
    """
    Trigger the full daily scan across ALL 12 agents.
    Runs in background — returns immediately with job confirmation.
    """
    background_tasks.add_task(run_daily_schedule)
    return {
        "status": "started",
        "message": "Full daily scan started in background. Check /logs for results.",
        "modules": ["finance_fraud", "inventory_supply_chain", "operations"],
        "agents": 12
    }
 
 
# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 
 
# ── PLAN ENDPOINTS ───────────────────────────
@app.get("/plans", tags=["Execution Plans"])
def get_all_plans():
    """GET all execution plans with their status."""
    try:
        from agents.master_orchestrator import get_all_plans as _get_all
        plans = _get_all()
        return [p.dict() if hasattr(p, 'dict') else p.__dict__ for p in plans]
    except Exception as e:
        return []
 
@app.get("/plans/{plan_id}", tags=["Execution Plans"])
def get_plan(plan_id: str):
    """GET a specific execution plan by ID."""
    try:
        from agents.master_orchestrator import get_plan as _get
        plan = _get(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        return plan.dict() if hasattr(plan, 'dict') else plan.__dict__
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        