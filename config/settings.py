"""
config/settings.py
Central configuration — Groq LLM setup, shared memory, logging
FIXED: llama-3.3-70b-versatile (llama3-70b-8192 decommissioned)
"""
 
import os
import time
from dotenv import load_dotenv
from crewai import LLM
from loguru import logger
import sys
 
load_dotenv()
 
# ─────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────
 
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> — {message}",
    level=os.getenv("LOG_LEVEL", "INFO"),
    colorize=True
)
 
import os
os.makedirs("logs", exist_ok=True)
 
logger.add(
    "logs/system.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)
 
# ─────────────────────────────────────────────
# GROQ LLM — Free, Fast, Reliable
# ─────────────────────────────────────────────
 
def get_llm(temperature: float = 0.1, max_tokens: int = 512):
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash-lite")
    
    time.sleep(35)  # 10 RPM ke liye 35 sec wait
    
    return LLM(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=300,
        timeout=60,
    )   

# ─────────────────────────────────────────────
# SYSTEM SETTINGS
# ─────────────────────────────────────────────
 
class Settings:
    # LLM
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash-lite")

    # Database
    DATABASE_URL             = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/multi_agent_db")
 
    # Redis
    REDIS_HOST               = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT               = int(os.getenv("REDIS_PORT", 6379))
 
    # Agent behavior
    MAX_ITERATIONS           = int(os.getenv("MAX_AGENT_ITERATIONS", 10))
    AGENT_TIMEOUT_SECONDS          = int(os.getenv("AGENT_TIMEOUT_SECONDS", 60))
    ENABLE_HUMAN_APPROVAL    = os.getenv("ENABLE_HUMAN_APPROVAL", "false").lower() == "true"
 
    # Thresholds
    FRAUD_AMOUNT_THRESHOLD   = float(os.getenv("FRAUD_AMOUNT_THRESHOLD", 10000))
    FRAUD_VELOCITY_THRESHOLD = int(os.getenv("FRAUD_VELOCITY_THRESHOLD", 5))
    LOW_STOCK_THRESHOLD      = int(os.getenv("LOW_STOCK_THRESHOLD", 20))
    AUTO_ORDER_THRESHOLD     = int(os.getenv("AUTO_ORDER_THRESHOLD", 10))
 
    # Alerts (optional)
 
settings = Settings()