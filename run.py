"""
run.py
Quick test runner — test any agent directly from command line without starting the API.
 
Usage:
    python run.py                          # Run interactive menu
    python run.py --module customer        # Run customer service demo
    python run.py --module inventory       # Run inventory check
    python run.py --module finance         # Run finance + fraud scan
    python run.py --module operations      # Run HR + Sales + IT
    python run.py --module all             # Run full daily scan
    python run.py --ask "your problem"     # Ask orchestrator anything
"""
 
import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from loguru import logger
 
console = Console()
 
 
def print_banner():
    console.print(Panel.fit(
        "[bold cyan]🤖 Multi-Agent Business System[/bold cyan]\n"
        "[dim]12 Agents · 7 Modules · Groq LLaMA3 + CrewAI + LangChain · PostgreSQL[/dim]",
        border_style="cyan"
    ))
 
 
def print_menu():
    table = Table(title="Available Modules", border_style="blue")
    table.add_column("No.", style="cyan", width=5)
    table.add_column("Module", style="green")
    table.add_column("Agents", style="yellow")
    table.add_column("What it does")
 
    table.add_row("1", "Customer Service", "Support + Sentiment",    "Handle complaints, create tickets, analyze mood")
    table.add_row("2", "Inventory",        "Inventory + Supply Chain","Check stock, predict demand, place orders")
    table.add_row("3", "Finance",          "Finance + Fraud",         "Generate reports, detect fraud, track cash flow")
    table.add_row("4", "Operations",       "HR + Sales + IT",         "Performance, pipeline, system health")
    table.add_row("5", "Full Scan",        "All 12 Agents",           "Run everything — complete daily scan")
    table.add_row("6", "Ask Orchestrator", "Master Orchestrator",     "Type any business problem in plain language")
    table.add_row("0", "Exit",             "—",                       "Quit the system")
 
    console.print(table)
 
 
def run_module(choice: str, custom_request: str = None):
    console.print(f"\n[cyan]Starting module: {choice}...[/cyan]\n")
 
    try:
        if choice in ["1", "customer"]:
            from agents.customer_service_agents import run_customer_service_crew
            customer_id = Prompt.ask("Customer ID", default="CUST-001")
            complaint   = Prompt.ask("Customer complaint", default="My order arrived damaged and I want a refund immediately!")
            result = run_customer_service_crew(customer_id, complaint)
 
        elif choice in ["2", "inventory"]:
            from agents.inventory_agents import run_inventory_crew
            result = run_inventory_crew()
 
        elif choice in ["3", "finance"]:
            from agents.finance_agents import run_finance_crew
            result = run_finance_crew()
 
        elif choice in ["4", "operations"]:
            from agents.remaining_agents import run_operations_crew
            result = run_operations_crew()
 
        elif choice in ["5", "all"]:
            from agents.master_orchestrator import run_daily_schedule
            result = run_daily_schedule()
 
        elif choice in ["6", "ask"]:
            from agents.master_orchestrator import process_business_request
            if custom_request:
                request = custom_request
            else:
                request = Prompt.ask("\n[green]Describe your business problem[/green]")
            result = process_business_request(request)
 
        else:
            console.print("[red]Invalid choice![/red]")
            return
 
        console.print(Panel(
            str(result)[:3000],
            title="[green]✅ Agent Result[/green]",
            border_style="green"
        ))
 
    except Exception as e:
        console.print(Panel(
            f"[red]Error: {e}[/red]\n\n"
            "[yellow]Make sure:\n"
            "1. GROQ_API_KEY is set in .env\n"
            "2. PostgreSQL is running\n"
            "3. Run: pip install -r requirements.txt[/yellow]",
            title="❌ Error",
            border_style="red"
        ))
 
 
def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Business System Runner")
    parser.add_argument("--module", type=str, help="Module to run: customer/inventory/finance/operations/all/ask")
    parser.add_argument("--ask",    type=str, help="Send a business problem to the orchestrator")
    args = parser.parse_args()
 
    print_banner()
 
    # CLI arguments
    if args.ask:
        run_module("ask", args.ask)
        return
 
    if args.module:
        run_module(args.module)
        return
 
    # Interactive menu
    while True:
        console.print()
        print_menu()
        choice = Prompt.ask("\n[cyan]Select module[/cyan]", default="6")
 
        if choice == "0":
            console.print("[yellow]Goodbye! 👋[/yellow]")
            sys.exit(0)
 
        run_module(choice)
        console.print("\n[dim]Press Enter to return to menu...[/dim]")
        input()
 
 
if __name__ == "__main__":
    main()