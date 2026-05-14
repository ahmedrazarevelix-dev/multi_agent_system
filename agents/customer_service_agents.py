"""
agents/customer_service_agents.py
Module 1 — Customer Support Agent + Sentiment Analysis Agent
"""
 
import uuid
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from loguru import logger
 
from config.settings import get_llm, settings
from database.models import get_session, Customer, SupportTicket, TicketStatus
from tools.shared_tools import log_agent_action, send_alert, new_id, now_str
 
 
# ─────────────────────────────────────────────
# TOOLS — Customer Service (BaseTool classes)
# ─────────────────────────────────────────────
 
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
            logger.success(f"Ticket created: {ticket_id}")
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
 
        angry_count    = sum(1 for w in angry_words    if w in text_lower)
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
 
 
# Tool instances
get_customer_history  = GetCustomerHistoryTool()
create_support_ticket = CreateSupportTicketTool()
resolve_ticket        = ResolveTicketTool()
analyze_sentiment     = AnalyzeSentimentTool()
 
 
# ─────────────────────────────────────────────
# AGENT 1 — Customer Support Agent
# ─────────────────────────────────────────────
 
def create_support_agent():
    llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Customer Support Specialist",
        goal=(
            "Resolve customer issues quickly and professionally. "
            "Retrieve customer history, draft helpful responses, create tickets, "
            "and ensure every customer leaves satisfied."
        ),
        backstory=(
            "You are a seasoned customer support expert with 10 years of experience. "
            "You always check customer history before responding, you are empathetic, "
            "solution-focused, and you escalate critical issues immediately."
        ),
        tools=[get_customer_history, create_support_ticket, resolve_ticket, log_agent_action],
        llm=llm,
        verbose=False,
        max_iter=settings.MAX_ITERATIONS,
        allow_delegation=False,
    )
 
 
# ─────────────────────────────────────────────
# AGENT 2 — Sentiment Analysis Agent
# ─────────────────────────────────────────────
 
def create_sentiment_agent():
    llm = get_llm(temperature=0.0)
    return Agent(
        role="Customer Sentiment Analyst",
        goal=(
            "Analyze customer communications for sentiment and emotional tone. "
            "Flag angry or distressed customers immediately and recommend priority levels."
        ),
        backstory=(
            "You are an expert in natural language processing and customer psychology. "
            "You detect emotional cues, escalation risks, and patterns in customer feedback. "
            "Your alerts help the team prevent customer churn before it happens."
        ),
        tools=[analyze_sentiment, send_alert, log_agent_action],
        llm=llm,
        verbose=False,
        max_iter=settings.MAX_ITERATIONS,
        allow_delegation=False,
    )
 
 
# ─────────────────────────────────────────────
# CREW — Customer Service Module
# ─────────────────────────────────────────────
 
def run_customer_service_crew(customer_id: str, complaint: str) -> str:
    """
    Run the full customer service workflow for a complaint.
    1. Sentiment agent analyzes the message
    2. Support agent retrieves history + creates ticket + drafts response
    """
    logger.info(f"Starting Customer Service Crew for customer: {customer_id}")
 
    support_agent   = create_support_agent()
    sentiment_agent = create_sentiment_agent()
 
    task1 = Task(
        description=f"""
        Analyze the sentiment and urgency of this customer message:
        Customer ID: {customer_id}
        Message: "{complaint}"
 
        Determine:
        1. Sentiment (positive/neutral/negative/angry)
        2. Urgency level (low/medium/high/critical)
        3. Should this be escalated immediately?
        4. Recommended priority level
 
        Use the analyze_sentiment tool, then send an alert if urgency is high or critical.
        """,
        agent=sentiment_agent,
        expected_output="Sentiment report with urgency level and escalation recommendation."
    )
 
    task2 = Task(
        description=f"""
        Handle this customer complaint end-to-end:
        Customer ID: {customer_id}
        Complaint: "{complaint}"
 
        Steps:
        1. Get the customer's account history using get_customer_history
        2. Draft a professional, empathetic response addressing their complaint
        3. Create a support ticket with create_support_ticket
        4. Log the action using log_agent_action
        5. Return a summary of what was done
 
        Be specific, helpful, and reference their account history in your response.
        """,
        agent=support_agent,
        expected_output="Complete resolution summary with ticket ID and drafted response.",
        context=[task1]
    )
 
    crew = Crew(
        agents=[sentiment_agent, support_agent],
        tasks=[task1, task2],
        verbose=False
    )
 
    result = crew.kickoff()
    logger.success(f"Customer Service Crew completed for {customer_id}")
    return str(result)