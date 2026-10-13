import hmac, hashlib, base64, json, os
import requests
import os
from ..config import WEBHOOK_SECRET

def verify_signature(raw_body: bytes, signature: str) -> bool:
    expected = base64.b64encode(hmac.new(WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(expected, signature or "")

# Schemas
def map_customer(p: dict) -> dict:
    billing = p.get("billing") or {}
    return {"woo_id": p["id"], "email": billing.get("email",""), "name": (billing.get("first_name","")+" "+billing.get("last_name","")).strip(),
            "orders_count": p.get("orders_count",0), "total_spent": float(p.get("total_spent",0) or 0)}

def map_order(p: dict) -> dict:
    b = p.get("billing") or {}
    return {"woo_id": p["id"], "customer_woo_id": (p.get("customer_id") or (p.get("customer") or {}).get("id")),
            "status": p.get("status","pending"), "total": float(p.get("total",0) or 0),
            "currency": p.get("currency","USD"), "buyer_email": b.get("email","")}

class MockWooClient:
    def list_customers(self): return []
    def list_orders(self, status=None): return []

class RealWooClient(MockWooClient):
    def __init__(self):
        try:
            from woocommerce import API
        except Exception:
            raise RuntimeError("woocommerce package not installed")
        import os
        self.api = API(url=os.getenv("WC_BASE_URL"), consumer_key=os.getenv("WC_CONSUMER_KEY"), consumer_secret=os.getenv("WC_CONSUMER_SECRET"), version="wc/v3")
    def list_customers(self):
        return self.api.get("customers").json()
    def list_orders(self, status=None):
        params={"status": status} if status else {}
        return self.api.get("orders", params=params).json()

class WooClient(MockWooClient):
    def __init__(self, base_url="", key="", secret=""):
        self.base_url = base_url.rstrip("/")
        self.auth = (key, secret)
    def list_customers(self):
        r = requests.get(f"{self.base_url}/wp-json/wc/v3/customers", auth=self.auth, timeout=10)
        r.raise_for_status(); return r.json()
    def list_orders(self, status=None):
        params = {"status": status} if status else {}
        r = requests.get(f"{self.base_url}/wp-json/wc/v3/orders", auth=self.auth, params=params, timeout=10)
        r.raise_for_status(); return r.json()

def woo_client():
    import os
    if os.getenv("WC_BASE_URL") and os.getenv("WC_CONSUMER_KEY") and os.getenv("WC_CONSUMER_SECRET"):
        try:
            return RealWooClient()
        except Exception:
            return MockWooClient()
    url = os.getenv("WOO_URL","")
    if url:
        return WooClient(url, os.getenv("WOO_KEY",""), os.getenv("WOO_SECRET",""))
    return MockWooClient()
"adapter"