import os, hmac, hashlib, base64, json
os.environ["DATABASE_URL"]="sqlite:///./e2e.db"
os.environ["WOOCOMMERCE_WEBHOOK_SECRET"]="dev-secret"
from fastapi.testclient import TestClient
from app.main import app
from app.db import engine, Base

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
client=TestClient(app)

def sign(body):
    return base64.b64encode(hmac.new(b"dev-secret", body, hashlib.sha256).digest()).decode()

def test_webhook_and_update():
    payload={"id":1001,"customer_id":42,"status":"processing","total":"50.0","currency":"USD","billing":{"email":"jane@example.com","first_name":"Jane","last_name":"Doe"}}
    raw=json.dumps(payload).encode()
    r=client.post("/webhook/woocommerce", content=raw, headers={"X-WC-Webhook-Signature":sign(raw),"X-WC-Webhook-Topic":"order.created"})
    assert r.status_code==200
    assert client.get("/orders").json()[0]["woo_id"]==1001
    # duplicate
    r2=client.post("/webhook/woocommerce", content=raw, headers={"X-WC-Webhook-Signature":sign(raw),"X-WC-Webhook-Topic":"order.created"})
    assert r2.status_code==200
    # status update
    upd=dict(payload,status="shipped")
    raw2=json.dumps(upd).encode()
    r3=client.post("/webhook/woocommerce", content=raw2, headers={"X-WC-Webhook-Signature":sign(raw2),"X-WC-Webhook-Topic":"order.updated"})
    assert r3.status_code==200
    msgs=client.get("/messages").json()
    assert len(msgs)>=1
    # bad signature
    r4=client.post("/webhook/woocommerce", content=raw, headers={"X-WC-Webhook-Signature":"bad","X-WC-Webhook-Topic":"order.created"})
    assert r4.status_code==401