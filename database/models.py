"""
database/models.py
PostgreSQL database models and connection setup for Multi-Agent System
"""
 
from sqlalchemy import (
    create_engine, Column, String, Integer, Float,
    DateTime, Boolean, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import os
from dotenv import load_dotenv
from loguru import logger
from base import Base
 
load_dotenv()
 
# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────
 
class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
 
class OrderStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
 
class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
 
# ─────────────────────────────────────────────
# MODULE 1 — CUSTOMER SERVICE
# ─────────────────────────────────────────────
 
class Customer(Base):
    __tablename__ = "customers"
    id            = Column(String, primary_key=True)
    name          = Column(String(200), nullable=False)
    email         = Column(String(200), unique=True)
    phone         = Column(String(50))
    account_type  = Column(String(50), default="standard")
    created_at    = Column(DateTime, default=func.now())
    tickets       = relationship("SupportTicket", back_populates="customer")
    transactions  = relationship("Transaction", back_populates="customer")
 
 
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id            = Column(String, primary_key=True)
    customer_id   = Column(String, ForeignKey("customers.id"))
    subject       = Column(String(500))
    description   = Column(Text)
    status        = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    sentiment     = Column(String(50))
    sentiment_score = Column(Float)
    ai_response   = Column(Text)
    resolved_at   = Column(DateTime)
    created_at    = Column(DateTime, default=func.now())
    updated_at    = Column(DateTime, default=func.now(), onupdate=func.now())
    customer      = relationship("Customer", back_populates="tickets")
 
 
# ─────────────────────────────────────────────
# MODULE 2 — INVENTORY & SUPPLY CHAIN
# ─────────────────────────────────────────────
 
class Product(Base):
    __tablename__ = "products"
    id            = Column(String, primary_key=True)
    name          = Column(String(300), nullable=False)
    sku           = Column(String(100), unique=True)
    category      = Column(String(100))
    current_stock = Column(Integer, default=0)
    min_stock     = Column(Integer, default=20)
    reorder_point = Column(Integer, default=10)
    unit_cost     = Column(Float)
    unit_price    = Column(Float)
    supplier_id   = Column(String, ForeignKey("suppliers.id"))
    created_at    = Column(DateTime, default=func.now())
    updated_at    = Column(DateTime, default=func.now(), onupdate=func.now())
    supplier      = relationship("Supplier", back_populates="products")
 
 
class Supplier(Base):
    __tablename__ = "suppliers"
    id              = Column(String, primary_key=True)
    name            = Column(String(300), nullable=False)
    country         = Column(String(100))
    lead_time_days  = Column(Integer)
    reliability_score = Column(Float, default=1.0)
    price_index     = Column(Float, default=1.0)
    contact_email   = Column(String(200))
    created_at      = Column(DateTime, default=func.now())
    products        = relationship("Product", back_populates="supplier")
    orders          = relationship("SupplyOrder", back_populates="supplier")
 
 
class SupplyOrder(Base):
    __tablename__ = "supply_orders"
    id            = Column(String, primary_key=True)
    supplier_id   = Column(String, ForeignKey("suppliers.id"))
    product_id    = Column(String, ForeignKey("products.id"))
    quantity      = Column(Integer)
    unit_cost     = Column(Float)
    total_cost    = Column(Float)
    status        = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    expected_date = Column(DateTime)
    ai_generated  = Column(Boolean, default=True)
    notes         = Column(Text)
    created_at    = Column(DateTime, default=func.now())
    supplier      = relationship("Supplier", back_populates="orders")
 
 
# ─────────────────────────────────────────────
# MODULE 3 — FINANCE & FRAUD
# ─────────────────────────────────────────────
 
class Transaction(Base):
    __tablename__ = "transactions"
    id            = Column(String, primary_key=True)
    customer_id   = Column(String, ForeignKey("customers.id"))
    amount        = Column(Float, nullable=False)
    currency      = Column(String(10), default="USD")
    type          = Column(String(50))
    status        = Column(String(50), default="completed")
    is_flagged    = Column(Boolean, default=False)
    fraud_score   = Column(Float, default=0.0)
    risk_level    = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    extra_data      = Column(JSON)
    created_at    = Column(DateTime, default=func.now())
    customer      = relationship("Customer", back_populates="transactions")
 
 
class FinancialReport(Base):
    __tablename__ = "financial_reports"
    id            = Column(String, primary_key=True)
    report_type   = Column(String(100))
    period_start  = Column(DateTime)
    period_end    = Column(DateTime)
    total_revenue = Column(Float)
    total_expenses = Column(Float)
    net_profit    = Column(Float)
    report_data   = Column(JSON)
    ai_insights   = Column(Text)
    created_at    = Column(DateTime, default=func.now())
 
 
# ─────────────────────────────────────────────
# MODULE 4 — HR
# ─────────────────────────────────────────────
 
class Employee(Base):
    __tablename__ = "employees"
    id            = Column(String, primary_key=True)
    name          = Column(String(200), nullable=False)
    department    = Column(String(100))
    role          = Column(String(200))
    email         = Column(String(200))
    hire_date     = Column(DateTime)
    salary        = Column(Float)
    performance_score = Column(Float)
    created_at    = Column(DateTime, default=func.now())
 
 
class JobApplication(Base):
    __tablename__ = "job_applications"
    id            = Column(String, primary_key=True)
    position      = Column(String(200))
    applicant_name = Column(String(200))
    email         = Column(String(200))
    cv_text       = Column(Text)
    ai_score      = Column(Float)
    ai_summary    = Column(Text)
    status        = Column(String(50), default="pending")
    created_at    = Column(DateTime, default=func.now())
 
 
# ─────────────────────────────────────────────
# MODULE 5 — SALES & MARKETING
# ─────────────────────────────────────────────
 
class Lead(Base):
    __tablename__ = "leads"
    id            = Column(String, primary_key=True)
    name          = Column(String(200))
    email         = Column(String(200))
    company       = Column(String(200))
    source        = Column(String(100))
    qualification_score = Column(Float, default=0.0)
    status        = Column(String(50), default="new")
    ai_notes      = Column(Text)
    created_at    = Column(DateTime, default=func.now())
 
 
# ─────────────────────────────────────────────
# AGENT AUDIT LOG (All agents log here)
# ─────────────────────────────────────────────
 
class AgentLog(Base):
    __tablename__ = "agent_logs"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    agent_name    = Column(String(100), nullable=False)
    task          = Column(Text)
    result        = Column(Text)
    status        = Column(String(50))
    duration_ms   = Column(Integer)
    tokens_used   = Column(Integer)
    created_at    = Column(DateTime, default=func.now())
 
 
# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────
 
def get_engine():
    url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/multi_agent_db")
    return create_engine(url, pool_pre_ping=True, pool_size=10, max_overflow=20)
 
 
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
 
 
def init_db():
    """Create all tables if they don't exist"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.success("Database tables created successfully!")
 
 
if __name__ == "__main__":
    init_db()