"""
fix_tools.py
============
Yeh script run karo apne PC pe:
    py -3.11 fix_tools.py
 
Yeh script sab agent files mein @tool decorator ko
crewai BaseTool se compatible banata hai.
"""
 
import os
import sys
 
AGENTS_DIR = os.path.join(os.path.dirname(__file__), "agents")
 
# ── 1. customer_service_agents.py fix ──────────────
CUSTOMER_FIX = '''"""
agents/customer_service_agents.py
Module 1 — Customer Support Agent + Sentiment Analysis Agent
Fixed for CrewAI latest version
"""
 
import uuid
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from loguru import logger
 
from config.settings import get_llm, settings
from database.models import get_session, Customer, SupportTicket, TicketStatus
from tools.shared_tools import log_agent_action, send_alert, new_id, now_str
 
 
class GetCustomerHistoryTool(BaseTool):
    name: str = "get_customer_history"
    description: str = "Retrieve full account history for a customer. Provide: customer_id"
 
    def _run(self, customer_id: str = "") -> str:
        try:
            session = get_session()
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return f"No customer found with ID: {customer_id}"
            tickets = session.query(SupportTicket).filter_by(customer_id=customer_id).limit(10).all()
            history = {
                "customer_name": customer.name,
                "email": customer.email,
                "account_type": customer.account_type,
                "total_tickets": len(tickets),
                "recent_issues": [
                    {"subject": t.subject, "status": t.status.value, "date": str(t.created_at)}
                    for t in tickets
                ]
            }
            session.close()
            return str(history)
        except Exception as e:
            return f"Error fetching history: {e}"
 
 
class CreateSupportTicketTool(BaseTool):
    name: str = "create_support_ticket"
    description: str = "Create a new support ticket. Provide: customer_id, subject, description, ai_response"
 
    def _run(self, customer_id: str = "", subject: str = "",
             description: str = "", ai_response: str = "") -> str:
        try:
            session = get_session()
            ticket = SupportTicket(
                id=new_id(),
                customer_id=customer_id,
                subject=subject,
                description=description,
                ai_response=ai_response,
                status=TicketStatus.IN_PROGRESS
            )
            session.add(ticket)
            session.commit()
            ticket_id = ticket.id
            session.close()
            return f"Ticket {ticket_id} created successfully."
        except Exception as e:
            return f"Error creating ticket: {e}"
 
 
class ResolveTicketTool(BaseTool):
    name: str = "resolve_ticket"
    description: str = "Mark a support ticket as resolved. Provide: ticket_id, resolution"
 
    def _run(self, ticket_id: str = "", resolution: str = "") -> str:
        try:
            session = get_session()
            ticket = session.query(SupportTicket).filter_by(id=ticket_id).first()
            if not ticket:
                return f"Ticket {ticket_id} not found"
            ticket.status = TicketStatus.RESOLVED
            ticket.ai_response = resolution
            ticket.resolved_at = datetime.utcnow()
            session.commit()
            session.close()
            return f"Ticket {ticket_id} resolved."
        except Exception as e:
            return f"Error: {e}"
 
 
class AnalyzeSentimentTool(BaseTool):
    name: str = "analyze_sentiment"
    description: str = "Analyze sentiment of customer text. Provide: text"
 
    def _run(self, text: str = "") -> str:
        text_lower = text.lower()
        angry_words    = ["terrible","horrible","worst","useless","awful","furious","scam","fraud"]
        negative_words = ["bad","disappointed","unhappy","problem","issue","broken","fail","wrong"]
        positive_words = ["great","excellent","happy","satisfied","perfect","love","wonderful","thank"]
 
        angry_count    = sum(1 for w in angry_words   if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        positive_count = sum(1 for w in positive_words if w in text_lower)
 
        if angry_count >= 2:
            return "ANGRY | score: 0.9 | Immediate escalation recommended"
        elif angry_count == 1 or negative_count >= 2:
            return "NEGATIVE | score: 0.65 | Priority handling needed"
        elif positive_count >= 2:
            return "POSITIVE | score: 0.85 | Standard response sufficient"
        else:
            return "NEUTRAL | score: 0.5 | Standard response sufficient"
 
 
get_customer_history  = GetCustomerHistoryTool()
create_support_ticket = CreateSupportTicketTool()
resolve_ticket        = ResolveTicketTool()
analyze_sentiment     = AnalyzeSentimentTool()
 
 
def create_support_agent():
    llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Customer Support Specialist",
        goal="Resolve customer issues quickly. Retrieve history, draft responses, create tickets.",
        backstory="10 years customer support experience. Always empathetic and solution-focused.",
        tools=[get_customer_history, create_support_ticket, resolve_ticket, log_agent_action],
        llm=llm, verbose=False, max_iter=settings.MAX_ITERATIONS, allow_delegation=False,
    )
 
 
def create_sentiment_agent():
    llm = get_llm(temperature=0.0)
    return Agent(
        role="Customer Sentiment Analyst",
        goal="Analyze customer sentiment. Flag angry customers immediately.",
        backstory="Expert in NLP and customer psychology. Detects escalation risks instantly.",
        tools=[analyze_sentiment, send_alert, log_agent_action],
        llm=llm, verbose=False, max_iter=settings.MAX_ITERATIONS, allow_delegation=False,
    )
 
 
def run_customer_service_crew(customer_id: str, complaint: str) -> str:
    support_agent   = create_support_agent()
    sentiment_agent = create_sentiment_agent()
 
    task1 = Task(
        description=f"""
        Analyze sentiment of this customer message:
        Customer ID: {customer_id}
        Message: "{complaint}"
        Use analyze_sentiment tool. Send alert if urgency is high or critical.
        """,
        agent=sentiment_agent,
        expected_output="Sentiment report with urgency level."
    )
 
    task2 = Task(
        description=f"""
        Handle this customer complaint:
        Customer ID: {customer_id}
        Complaint: "{complaint}"
        Steps: 1) get_customer_history 2) draft response 3) create_support_ticket 4) log_agent_action
        """,
        agent=support_agent,
        expected_output="Resolution summary with ticket ID.",
        context=[task1]
    )
 
    crew = Crew(agents=[sentiment_agent, support_agent], tasks=[task1, task2], verbose=False)
    result = crew.kickoff()
    return str(result)
'''
 
# ── Write fixed files ───────────────────────
files_to_write = {
    "agents/customer_service_agents.py": CUSTOMER_FIX,
}
 
print("Fixing agent files...")
for filepath, content in files_to_write.items():
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Fixed: {filepath}")
 
print("\nDone! Ab server restart karo:")
print("  set PYTHONPATH=C:\\Users\\Lenovo\\Desktop\\multi_agent_system")
print("  py -3.11 -m uvicorn main:app --reload --port 8000")
 