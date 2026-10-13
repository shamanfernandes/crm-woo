import os
from dotenv import load_dotenv

load_dotenv()

def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)

DATABASE_URL = get("DATABASE_URL", "sqlite:///./crm.db")
WEBHOOK_SECRET = get("WOOCOMMERCE_WEBHOOK_SECRET", "dev-secret")
ANTHROPIC_API_KEY = get("ANTHROPIC_API_KEY")
SMTP_ENABLED = get("SMTP_ENABLED", "false").lower() == "true"
CRM_MODE = get("CRM_MODE", "rule")
"config"