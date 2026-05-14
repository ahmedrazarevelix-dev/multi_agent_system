"""
agents/inventory_agents.py
Module 2 — Inventory Management Agent + Supply Chain Optimizer Agent
"""
 
import json
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool       
from loguru import logger
 
from config.settings import get_llm, settings
from database.models import get_session, Product, Supplier, SupplyOrder, OrderStatus
from tools.shared_tools import log_agent_action, send_alert, new_id
 
 
# ─────────────────────────────────────────────
# TOOLS — Inventory
# ─────────────────────────────────────────────
 
def get_low_stock_products() -> str:
    """Get all products that are below minimum stock threshold."""
    try:
        session = get_session()
        products = session.query(Product).filter(
            Product.current_stock <= Product.min_stock
        ).all()
        result = []
        for p in products:
            result.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "current_stock": p.current_stock,
                "min_stock": p.min_stock,
                "reorder_point": p.reorder_point,
                "supplier_id": p.supplier_id,
                "unit_cost": p.unit_cost
            })
        session.close()
        if not result:
            return "All products are sufficiently stocked."
        return json.dumps(result)
    except Exception as e:
        return f"Error: {e}"
 
 
def update_stock_level(product_id: str, new_quantity: int, reason: str) -> str:
    """Update the stock level of a product and log the change."""
    try:
        session = get_session()
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            return f"Product {product_id} not found"
        old_qty = product.current_stock
        product.current_stock = new_quantity
        product.updated_at = datetime.utcnow()
        session.commit()
        session.close()
        return f"Stock updated: {product.name} | {old_qty} → {new_quantity} | Reason: {reason}"
    except Exception as e:
        return f"Error: {e}"
 
 
def place_supply_order(supplier_id: str, product_id: str, quantity: int, notes: str = "") -> str:
    """Automatically place a supply order when stock is critically low."""
    try:
        session = get_session()
        supplier = session.query(Supplier).filter_by(id=supplier_id).first()
        product  = session.query(Product).filter_by(id=product_id).first()
        if not supplier or not product:
            return "Supplier or product not found"
 
        expected = datetime.utcnow() + timedelta(days=supplier.lead_time_days)
        total    = quantity * product.unit_cost
 
        order = SupplyOrder(
            id=new_id(),
            supplier_id=supplier_id,
            product_id=product_id,
            quantity=quantity,
            unit_cost=product.unit_cost,
            total_cost=total,
            status=OrderStatus.PENDING,
            expected_date=expected,
            ai_generated=True,
            notes=notes
        )
        session.add(order)
        session.commit()
        order_id = order.id
        session.close()
        return (
            f"Order {order_id} placed!\n"
            f"Supplier: {supplier.name}\n"
            f"Product: {product.name}\n"
            f"Quantity: {quantity}\n"
            f"Total Cost: ${total:,.2f}\n"
            f"Expected Delivery: {expected.strftime('%Y-%m-%d')}"
        )
    except Exception as e:
        return f"Error placing order: {e}"
 
 
def predict_stock_demand(product_id: str, days_ahead: int = 30) -> str:
    """
    Predict stock demand for the next N days based on historical patterns.
    Returns recommended reorder quantity.
    """
    try:
        session = get_session()
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            return f"Product {product_id} not found"
 
        # Simplified demand model — in production: use ML time-series model
        daily_usage     = max(1, (product.min_stock * 2) // 30)
        predicted_usage = daily_usage * days_ahead
        safety_buffer   = int(predicted_usage * 0.2)
        recommended_qty = predicted_usage + safety_buffer
 
        session.close()
        return (
            f"Demand Forecast for {product.name}:\n"
            f"Daily usage estimate: {daily_usage} units\n"
            f"Predicted {days_ahead}-day usage: {predicted_usage} units\n"
            f"Safety buffer (20%): {safety_buffer} units\n"
            f"Recommended order quantity: {recommended_qty} units"
        )
    except Exception as e:
        return f"Error: {e}"
 
 
# ─────────────────────────────────────────────
# TOOLS — Supply Chain
# ─────────────────────────────────────────────
 
def compare_suppliers(product_id: str) -> str:
    """Compare all suppliers for a product by price, lead time, and reliability score."""
    try:
        session = get_session()
        product   = session.query(Product).filter_by(id=product_id).first()
        suppliers = session.query(Supplier).all()
        if not product:
            return f"Product {product_id} not found"
 
        comparison = []
        for s in suppliers:
            score = (
                (1 / max(s.lead_time_days, 1)) * 40
                + s.reliability_score * 40
                + (1 / max(s.price_index, 0.1)) * 20
            )
            comparison.append({
                "supplier_id": s.id,
                "name": s.name,
                "country": s.country,
                "lead_time_days": s.lead_time_days,
                "reliability": f"{s.reliability_score:.0%}",
                "price_index": s.price_index,
                "overall_score": round(score, 2)
            })
 
        session.close()
        comparison.sort(key=lambda x: x["overall_score"], reverse=True)
        return json.dumps(comparison)
    except Exception as e:
        return f"Error: {e}"
 
 
def check_supplier_risk(supplier_id: str) -> str:
    """
    Assess risk level for a specific supplier.
    Checks reliability score, lead times, and recent order history.
    """
    try:
        session = get_session()
        supplier = session.query(Supplier).filter_by(id=supplier_id).first()
        if not supplier:
            return f"Supplier {supplier_id} not found"
 
        risk_factors = []
        risk_level   = "LOW"
 
        if supplier.reliability_score < 0.7:
            risk_factors.append("Low reliability score")
            risk_level = "HIGH"
        elif supplier.reliability_score < 0.85:
            risk_factors.append("Below-average reliability")
            risk_level = "MEDIUM"
 
        if supplier.lead_time_days > 30:
            risk_factors.append("Long lead times")
            if risk_level != "HIGH":
                risk_level = "MEDIUM"
 
        session.close()
        return (
            f"Supplier: {supplier.name} ({supplier.country})\n"
            f"Risk Level: {risk_level}\n"
            f"Reliability: {supplier.reliability_score:.0%}\n"
            f"Lead Time: {supplier.lead_time_days} days\n"
            f"Risk Factors: {', '.join(risk_factors) if risk_factors else 'None identified'}"
        )
    except Exception as e:
        return f"Error: {e}"
 
 
def optimize_delivery_route(origin_country: str, destination: str, urgency: str) -> str:
    """
    Recommend the best delivery route/method based on urgency and cost.
    urgency: 'low' | 'medium' | 'high' | 'critical'
    """
    routes = {
        "critical": {
            "method": "Air Freight",
            "days": "2-3",
            "cost_multiplier": "4x",
            "recommendation": "Use for critical stock-outs only"
        },
        "high": {
            "method": "Express Sea + Air final mile",
            "days": "7-10",
            "cost_multiplier": "2.5x",
            "recommendation": "Good balance of speed and cost"
        },
        "medium": {
            "method": "Standard Sea Freight",
            "days": "15-25",
            "cost_multiplier": "1x",
            "recommendation": "Default for planned replenishments"
        },
        "low": {
            "method": "Economy Sea Freight (consolidated)",
            "days": "25-40",
            "cost_multiplier": "0.7x",
            "recommendation": "Best for non-urgent bulk orders"
        }
    }
    route = routes.get(urgency, routes["medium"])
    return (
        f"Route Optimization: {origin_country} → {destination}\n"
        f"Recommended Method: {route['method']}\n"
        f"Estimated Transit: {route['days']} days\n"
        f"Cost Factor: {route['cost_multiplier']}\n"
        f"Note: {route['recommendation']}"
    )
 
 
# ─────────────────────────────────────────────
# AGENT 3 — Inventory Management Agent
# ─────────────────────────────────────────────
 
def create_inventory_agent():
    llm = get_llm(temperature=0.1)
    return Agent(
        role="Inventory Management Specialist",
        goal=(
            "Monitor stock levels in real-time. Predict demand. "
            "Automatically trigger reorders when stock falls below thresholds. "
            "Prevent both stockouts and overstock situations."
        ),
        backstory=(
            "You are an expert inventory manager with deep knowledge of supply chain dynamics. "
            "You use data-driven forecasting to maintain optimal stock levels, "
            "reducing both storage costs and lost-sales from stockouts."
        ),
        tools=[_get_low_stock, _update_stock, _predict_demand,
               _place_order, send_alert, log_agent_action],
        llm=llm,
        verbose=False,
        allow_delegation=True,
    )
 
 
# ─────────────────────────────────────────────
# AGENT 4 — Supply Chain Optimizer Agent
# ─────────────────────────────────────────────
 
def create_supply_chain_agent():
    llm = get_llm(temperature=0.1)
    return Agent(
        role="Supply Chain Optimization Expert",
        goal=(
            "Optimize the entire supply chain for cost, speed, and reliability. "
            "Compare suppliers, detect risks, recommend optimal routes, "
            "and ensure business continuity under disruptions."
        ),
        backstory=(
            "You are a supply chain expert who has managed global logistics for Fortune 500 companies. "
            "You assess supplier risk, optimize routes, benchmark prices, "
            "and always have a backup plan when disruptions occur."
        ),
        tools=[_compare_suppliers, _check_risk, _optimize_route,
               send_alert, log_agent_action],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
 
 
# ─────────────────────────────────────────────
# CREW — Inventory & Supply Chain Module
# ─────────────────────────────────────────────
 
def run_inventory_crew() -> str:
    """
    Run the full inventory + supply chain optimization workflow.
    1. Inventory agent scans for low stock
    2. Supply chain agent optimizes replenishment orders
    """
    logger.info("Starting Inventory & Supply Chain Crew...")
 
    inventory_agent    = create_inventory_agent()
    supply_chain_agent = create_supply_chain_agent()
 
    task1 = Task(
        description="""
        Perform a complete inventory health check:
        1. Use get_low_stock_products to find all products below minimum stock
        2. For each low-stock product, use predict_stock_demand for 30 days
        3. Send an alert if any product is critically low (below reorder_point)
        4. Prepare a list of products that need immediate reordering
        5. Log your findings with log_agent_action
 
        Be thorough and prioritize by urgency.
        """,
        agent=inventory_agent,
        expected_output="Complete inventory health report with list of products requiring reorder."
    )
 
    task2 = Task(
        description="""
        Based on the inventory report, optimize the supply chain:
        1. For each product that needs reordering, use compare_suppliers to find the best supplier
        2. Use check_supplier_risk to verify supplier reliability
        3. Use optimize_delivery_route to recommend the best shipping method
        4. Place orders using place_supply_order for critical items
        5. Send alerts for any high-risk supplier situations
        6. Log all actions with log_agent_action
 
        Make cost-effective decisions while ensuring timely delivery.
        """,
        agent=supply_chain_agent,
        expected_output="Supply chain optimization report with orders placed and routes recommended.",
        context=[task1]
    )
 
    crew = Crew(
        agents=[inventory_agent, supply_chain_agent],
        tasks=[task1, task2],
        verbose=False
    )
 
    result = crew.kickoff()
    logger.success("Inventory & Supply Chain Crew completed!")
    return str(result)
 
 
# ─────────────────────────────────────────────
# BASETOOL WRAPPERS — CrewAI compatible
# ─────────────────────────────────────────────
 
class GetLowStockTool(BaseTool):
    name: str = "get_low_stock_products"
    description: str = "Get all products below minimum stock threshold. No input needed."
    def _run(self) -> str:
        return get_low_stock_products()
 
class UpdateStockTool(BaseTool):
    name: str = "update_stock_level"
    description: str = "Update stock level of a product. Provide: product_id, new_quantity, reason"
    def _run(self, product_id: str = "", new_quantity: int = 0, reason: str = "") -> str:
        return update_stock_level(product_id, new_quantity, reason)
 
class PlaceOrderTool(BaseTool):
    name: str = "place_supply_order"
    description: str = "Place a supply order. Provide: supplier_id, product_id, quantity, notes"
    def _run(self, supplier_id: str = "", product_id: str = "", quantity: int = 0, notes: str = "") -> str:
        return place_supply_order(supplier_id, product_id, quantity, notes)
 
class PredictDemandTool(BaseTool):
    name: str = "predict_stock_demand"
    description: str = "Predict stock demand for next N days. Provide: product_id, days_ahead"
    def _run(self, product_id: str = "", days_ahead: int = 30) -> str:
        return predict_stock_demand(product_id, days_ahead)
 
class CompareSuppliersTool(BaseTool):
    name: str = "compare_suppliers"
    description: str = "Compare suppliers for a product. Provide: product_id"
    def _run(self, product_id: str = "") -> str:
        return compare_suppliers(product_id)
 
class CheckSupplierRiskTool(BaseTool):
    name: str = "check_supplier_risk"
    description: str = "Check risk level of a supplier. Provide: supplier_id"
    def _run(self, supplier_id: str = "") -> str:
        return check_supplier_risk(supplier_id)
 
class OptimizeRouteTool(BaseTool):
    name: str = "optimize_delivery_route"
    description: str = "Recommend best delivery route. Provide: origin_country, destination, urgency (low/medium/high/critical)"
    def _run(self, origin_country: str = "", destination: str = "", urgency: str = "medium") -> str:
        return optimize_delivery_route(origin_country, destination, urgency)
 
# Instances
_get_low_stock       = GetLowStockTool()
_update_stock        = UpdateStockTool()
_place_order         = PlaceOrderTool()
_predict_demand      = PredictDemandTool()
_compare_suppliers   = CompareSuppliersTool()
_check_risk          = CheckSupplierRiskTool()
_optimize_route      = OptimizeRouteTool()