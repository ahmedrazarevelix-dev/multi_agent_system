"""
tests/seed_data.py
Seed the PostgreSQL database with sample data for testing all 12 agents.
Run: python tests/seed_data.py
"""
 
import sys
sys.path.append("..")
 
from database.models import (
    init_db, get_session,
    Customer, Product, Supplier, Transaction, Employee, Lead
)
from tools.shared_tools import new_id
from datetime import datetime, timedelta
import random
 
 
def seed_all():
    print("Initializing database...")
    init_db()
    session = get_session()
 
    # ── CUSTOMERS ────────────────────────────────
    print("Seeding customers...")
    customers = [
        Customer(id="CUST-001", name="Ahmed Khan",    email="ahmed@example.com",   phone="+92-300-1234567", account_type="premium"),
        Customer(id="CUST-002", name="Sara Malik",    email="sara@example.com",    phone="+92-321-7654321", account_type="standard"),
        Customer(id="CUST-003", name="Bilal Ahmed",   email="bilal@example.com",   phone="+92-333-1112222", account_type="premium"),
        Customer(id="CUST-004", name="Fatima Zahra",  email="fatima@example.com",  phone="+92-345-9998877", account_type="standard"),
        Customer(id="CUST-005", name="Usman Tariq",   email="usman@example.com",   phone="+92-312-5556666", account_type="enterprise"),
    ]
    for c in customers:
        existing = session.query(Customer).filter_by(id=c.id).first()
        if not existing:
            session.add(c)
 
    # ── SUPPLIERS ────────────────────────────────
    print("Seeding suppliers...")
    suppliers = [
        Supplier(id="SUP-001", name="AlphaSupply Co",    country="China",    lead_time_days=14, reliability_score=0.92, price_index=0.85, contact_email="alpha@supply.com"),
        Supplier(id="SUP-002", name="BetaGoods Ltd",     country="Turkey",   lead_time_days=7,  reliability_score=0.78, price_index=1.10, contact_email="beta@goods.com"),
        Supplier(id="SUP-003", name="Gamma Materials",   country="UAE",      lead_time_days=5,  reliability_score=0.95, price_index=1.20, contact_email="gamma@mat.com"),
        Supplier(id="SUP-004", name="Delta Parts Inc",   country="Germany",  lead_time_days=21, reliability_score=0.99, price_index=1.50, contact_email="delta@parts.com"),
    ]
    for s in suppliers:
        existing = session.query(Supplier).filter_by(id=s.id).first()
        if not existing:
            session.add(s)
 
    session.commit()
 
    # ── PRODUCTS ─────────────────────────────────
    print("Seeding products...")
    products = [
        Product(id="PROD-001", name="Laptop Pro X1",    sku="LP-X1-001", category="Electronics", current_stock=5,   min_stock=20, reorder_point=10, unit_cost=800.0,  unit_price=1200.0, supplier_id="SUP-001"),
        Product(id="PROD-002", name="Wireless Mouse",   sku="WM-002",    category="Accessories", current_stock=8,   min_stock=30, reorder_point=15, unit_cost=15.0,   unit_price=35.0,  supplier_id="SUP-002"),
        Product(id="PROD-003", name="Office Chair",     sku="OC-003",    category="Furniture",   current_stock=50,  min_stock=10, reorder_point=5,  unit_cost=120.0,  unit_price=299.0, supplier_id="SUP-003"),
        Product(id="PROD-004", name="USB-C Hub 7-port", sku="UC-H-004",  category="Accessories", current_stock=3,   min_stock=25, reorder_point=10, unit_cost=25.0,   unit_price=65.0,  supplier_id="SUP-001"),
        Product(id="PROD-005", name="Monitor 27 inch",  sku="MON-27-005",category="Electronics", current_stock=12,  min_stock=15, reorder_point=8,  unit_cost=200.0,  unit_price=450.0, supplier_id="SUP-004"),
    ]
    for p in products:
        existing = session.query(Product).filter_by(id=p.id).first()
        if not existing:
            session.add(p)
 
    # ── TRANSACTIONS ─────────────────────────────
    print("Seeding transactions...")
    types = ["sale", "sale", "sale", "expense", "refund"]
    for i in range(30):
        t = Transaction(
            id=new_id(),
            customer_id=random.choice(["CUST-001","CUST-002","CUST-003","CUST-004","CUST-005"]),
            amount=round(random.uniform(50, 5000), 2),
            type=random.choice(types),
            status="completed",
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        session.add(t)
 
    # Add 2 suspicious transactions for fraud testing
    session.add(Transaction(
        id=new_id(),
        customer_id="CUST-001",
        amount=15000.0,
        type="sale",
        status="completed",
        created_at=datetime.utcnow().replace(hour=3)  # 3am transaction
    ))
    session.add(Transaction(
        id=new_id(),
        customer_id="CUST-002",
        amount=25000.0,
        type="sale",
        status="completed",
        created_at=datetime.utcnow()
    ))
 
    # ── EMPLOYEES ────────────────────────────────
    print("Seeding employees...")
    employees = [
        Employee(id="EMP-001", name="Zara Hussain",  department="Engineering", role="Senior Developer",    email="zara@co.com",   performance_score=4.8, salary=120000),
        Employee(id="EMP-002", name="Hamza Raza",    department="Sales",       role="Sales Manager",       email="hamza@co.com",  performance_score=3.2, salary=80000),
        Employee(id="EMP-003", name="Nadia Shah",    department="Finance",     role="Financial Analyst",   email="nadia@co.com",  performance_score=4.5, salary=90000),
        Employee(id="EMP-004", name="Kamran Ali",    department="HR",          role="HR Specialist",       email="kamran@co.com", performance_score=2.8, salary=60000),
        Employee(id="EMP-005", name="Sana Mirza",    department="Marketing",   role="Digital Marketer",    email="sana@co.com",   performance_score=4.1, salary=70000),
        Employee(id="EMP-006", name="Tariq Mehmood", department="Engineering", role="DevOps Engineer",     email="tariq@co.com",  performance_score=4.6, salary=110000),
    ]
    for e in employees:
        existing = session.query(Employee).filter_by(id=e.id).first()
        if not existing:
            session.add(e)
 
    # ── SALES LEADS ──────────────────────────────
    print("Seeding sales leads...")
    leads = [
        Lead(id="LEAD-001", name="TechCorp Ltd",       email="ceo@techcorp.com",      company="TechCorp Ltd",   source="referral",      status="new"),
        Lead(id="LEAD-002", name="MegaRetail Inc",     email="procurement@mega.com",  company="MegaRetail Inc", source="demo_request",  status="new"),
        Lead(id="LEAD-003", name="SmallBiz Owner",     email="owner@gmail.com",       company="",               source="website",       status="new"),
        Lead(id="LEAD-004", name="Enterprise Solutions",email="cto@enterprise.com",   company="EntSol Corp",    source="inbound",       status="new"),
        Lead(id="LEAD-005", name="StartupXYZ",         email="founder@startupxyz.io", company="StartupXYZ",    source="conference",    status="new"),
    ]
    for l in leads:
        existing = session.query(Lead).filter_by(id=l.id).first()
        if not existing:
            session.add(l)
 
    session.commit()
    session.close()
    print("\n✅ All sample data seeded successfully!")
    print("You can now run: python run.py")
 
 
if __name__ == "__main__":
    seed_all()
 