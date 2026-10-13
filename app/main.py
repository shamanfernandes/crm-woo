from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .db import get_session, init_db
from .config import DEBUG
from .adapters.woocommerce import verify_signature
from .adapters.woocommerce import verify_signature
from .services.sync_service import sync_event
from .repositories.repos import CustomerRepo, OrderRepo, MessageRepo

app = FastAPI(title="CRM Woo")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    import os
    real = bool(os.getenv("WC_BASE_URL") and os.getenv("WC_CONSUMER_KEY") and os.getenv("WC_CONSUMER_SECRET"))
    return {"status":"ok","adapter": ("realwoo" if real else "mock")}

@app.post("/webhook/woocommerce")
async def webhook(request: Request, db: Session = Depends(get_session)):
    raw = await request.body()
    sig = request.headers.get("X-WC-Webhook-Signature","")
    if not verify_signature(raw, sig):
        raise HTTPException(401, "bad signature")
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(422, "bad payload")
    topic = request.headers.get("X-WC-Webhook-Topic","")
    # also allow topic in body
    if not topic:
        topic = payload.get("topic","order.created") if isinstance(payload, dict) else "order.created"
    if not isinstance(payload, dict):
        raise HTTPException(422, "bad payload")
    try:
        res = sync_event(db, topic, payload)
    except Exception as e:
        raise HTTPException(422, str(e))
    return {"ok": True, **res}

@app.post("/import")
def import_data(db: Session = Depends(get_session)):
    from .adapters.woocommerce import woo_client
    c = woo_client()
    n = 0
    for cust in c.list_customers():
        CustomerRepo(db).upsert(__import__("app.adapters.woocommerce", fromlist=["map_customer"]).map_customer(cust))
        n += 1
    for o in c.list_orders():
        from .adapters.woocommerce import map_order
        OrderRepo(db).upsert(map_order(o))
        n += 1
    return {"imported": n}

@app.get("/customers")
def customers(db: Session = Depends(get_session)):
    return [ {"woo_id": c.woo_id, "email": c.email, "name": c.name, "orders_count": c.orders_count, "total_spent": c.total_spent} for c in CustomerRepo(db).list()]

@app.get("/orders")
def orders(status: str = None, db: Session = Depends(get_session)):
    return [ {"woo_id": o.woo_id, "customer_woo_id": o.customer_woo_id, "status": o.status, "total": o.total, "currency": o.currency} for o in OrderRepo(db).list(status)]

@app.get("/messages")
def messages(db: Session = Depends(get_session)):
    return [ {"id": m.id, "to_email": m.to_email, "subject": m.subject, "body": m.body, "status": m.status, "channel": m.channel, "source": m.source, "trace": m.trace, "order_woo_id": m.order_woo_id} for m in MessageRepo(db).list()]

@app.post("/dev/simulate")
async def simulate(db: Session = Depends(get_session)):
    import json, hmac, hashlib, base64
    import os
    if os.getenv("DEBUG","false").lower()!="true":
        raise HTTPException(404, "not found")
    payload={"id":9999,"customer_id":7,"status":"shipped","total":"12.5","currency":"USD","billing":{"email":"sim@example.com","first_name":"Sim","last_name":"User"}}
    raw=json.dumps(payload).encode()
    # ensure customer
    from .services.sync_service import sync_event
    sync_event(db, "order.created", payload)
    return {"ok": True, "order_id": 9999}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
