import os
os.environ["DATABASE_URL"]="sqlite:///./e2e2.db"
os.environ["WOOCOMMERCE_WEBHOOK_SECRET"]="dev-secret"
from fastapi.testclient import TestClient
from app.db import Base, engine
from app.main import app
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
client=TestClient(app)
def test_health():
    r=client.get("/health"); assert r.status_code==200
def test_bad_sig():
    # missing signature
    r=client.post("/webhook/woocommerce", json={"id":1}, headers={"X-WC-Webhook-Topic":"order.created"})
    assert r.status_code==401

def test_malformed():
    import hmac,hashlib,base64,json
    secret=b"dev-secret"
    body=b"not-json"
    sig=base64.b64encode(hmac.new(secret,body,hashlib.sha256).digest()).decode()
    r=client.post("/webhook/woocommerce", content=body, headers={"X-WC-Webhook-Signature":sig,"X-WC-Webhook-Topic":"order.created","Content-Type":"application/json"})
    assert r.status_code in (400,422)
