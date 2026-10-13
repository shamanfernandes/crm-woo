import os
os.environ.setdefault("DATABASE_URL","sqlite:///./agent.db")
from app.db import Base, engine, SessionLocal, init_db
from app.repositories.repos import CustomerRepo
from app.models import Order
from app.agents.crm_agent import CRMAgent

def setup():
    Base.metadata.drop_all(engine)
    init_db()
    db=SessionLocal()
    CustomerRepo(db).upsert({"woo_id":42,"email":"j@x.com","name":"Jane","orders_count":2,"total_spent":600.0})
    o=Order(woo_id=100,customer_woo_id=42,status="shipped",total=50,currency="USD"); db.add(o); db.commit()
    return db,o

def test_rule_fallback():
    db,o=setup()
    try:
        agent=CRMAgent(db, llm=__import__("app.agents.llm_client",fromlist=["LLMClient"]).LLMClient(api_key="",base_url="https://x",model="m"))
        m=agent.handle_order_event(o, CustomerRepo(db).get(42), None)
        assert m is not None and m.source=="rule-based"
    finally:
        db.close()

class FakeLLM:
    available=lambda self: True
    def chat(self,messages,tools=None):
        if "tool" not in str(messages):
            return {"content":"","reasoning":"need data","tool_calls":[{"id":"1","function":{"name":"get_customer","arguments":"{\"woo_id\":42}"}}]}
        return {"content":"Hi repeat buyer","reasoning":"done","tool_calls":[]}

def test_tool_path():
    db,o=setup()
    db.query(__import__("app.models",fromlist=["Order"]).Order).filter_by(woo_id=100).update({"status":"processing"})
    db.commit()
    o=db.query(__import__("app.models",fromlist=["Order"]).Order).filter_by(woo_id=100).first()
    # change status so event triggers
    o.status="shipped"; db.commit()
    try:
        agent=CRMAgent(db, llm=FakeLLM())
        m=agent.handle_order_event(o, CustomerRepo(db).get(42), "processing")
        assert m is not None and m.source=="llm"
    finally:
        db.close()