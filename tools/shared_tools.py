"""
tools/shared_tools.py
Reusable tools — fixed for CrewAI latest version (BaseTool style)
"""
 
import uuid
import json
import os
from datetime import datetime
from loguru import logger
from crewai.tools import BaseTool
from database.models import get_session, AgentLog
 
 
# ─────────────────────────────────────────────
# PLAIN UTILITY FUNCTIONS
# ─────────────────────────────────────────────
 
def new_id() -> str:
    return str(uuid.uuid4())[:8].upper()
 
 
def now_str() -> str:
    return datetime.utcnow().isoformat()
 
 
# ─────────────────────────────────────────────
# TOOL CLASSES (CrewAI BaseTool — new API)
# ─────────────────────────────────────────────
 
class LogAgentActionTool(BaseTool):
    name: str = "log_agent_action"
    description: str = (
        "Log any agent action to the audit trail. "
        "Provide: agent_name, task, result, status (success/failed), duration_ms"
    )
 
    def _run(self, agent_name: str = "Agent", task: str = "",
             result: str = "", status: str = "success",
             duration_ms: int = 0) -> str:
        try:
            session = get_session()
            log = AgentLog(
                agent_name=agent_name,
                task=task[:500],
                result=str(result)[:2000],
                status=status,
                duration_ms=duration_ms
            )
            session.add(log)
            session.commit()
            session.close()
            return f"Logged: [{agent_name}] {task[:60]}"
        except Exception as e:
            logger.error(f"Log failed: {e}")
            return f"Log failed: {e}"
 
 
class SendAlertTool(BaseTool):
    name: str = "send_alert"
    description: str = (
        "Send an alert to the management team. "
        "level: info | warning | critical. "
        "Provide: level, subject, message"
    )
 
    def _run(self, level: str = "info",
             subject: str = "Alert",
             message: str = "") -> str:
        try:
            alert_msg = f"[{level.upper()}] {subject}: {message}"
            if level == "critical":
                logger.critical(alert_msg)
            else:
                logger.warning(alert_msg)
 
            os.makedirs("logs", exist_ok=True)
            with open("logs/alerts.log", "a", encoding="utf-8") as f:
                f.write(f"{now_str()} | {level.upper()} | {subject} | {message}\n")
 
            return f"Alert sent: {subject}"
        except Exception as e:
            return f"Alert failed: {e}"
 
 
class QueryDatabaseTool(BaseTool):
    name: str = "query_database"
    description: str = (
        "Execute a safe SELECT query on PostgreSQL. "
        "Only SELECT statements allowed. Provide: sql"
    )
 
    def _run(self, sql: str = "") -> str:
        if not sql.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries allowed."
        try:
            session = get_session()
            result  = session.execute(sql)
            rows    = [dict(row) for row in result]
            session.close()
            return json.dumps(rows[:50], default=str)
        except Exception as e:
            return f"Query error: {e}"
 
 
class GetDatetimeTool(BaseTool):
    name: str = "get_current_datetime"
    description: str = "Returns the current UTC date and time."
 
    def _run(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
 
 
class ParseSummarizeTool(BaseTool):
    name: str = "parse_and_summarize"
    description: str = "Parse JSON data and return a readable summary. Provide: data, focus (optional)"
 
    def _run(self, data: str = "", focus: str = "") -> str:
        try:
            parsed = json.loads(data)
            if isinstance(parsed, list):
                summary = f"Found {len(parsed)} records."
                if focus:
                    summary += f" Focus: {focus}"
                if parsed:
                    summary += f" Sample: {json.dumps(parsed[0], default=str)}"
            else:
                summary = json.dumps(parsed, indent=2, default=str)[:500]
            return summary
        except Exception:
            return str(data)[:500]
 
 
# ─────────────────────────────────────────────
# INSTANCES — import these in all agent files
# ─────────────────────────────────────────────
 
log_agent_action     = LogAgentActionTool()
send_alert           = SendAlertTool()
query_database       = QueryDatabaseTool()
get_current_datetime = GetDatetimeTool()
parse_and_summarize  = ParseSummarizeTool()
 