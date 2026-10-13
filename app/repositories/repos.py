from sqlalchemy.orm import Session
from ..models import Customer, Order, Message

class CustomerRepo:
    def __init__(self, db: Session): self.db = db
    def upsert(self, data: dict):
        c = self.db.query(Customer).filter(Customer.woo_id == data["woo_id"]).first()
        if not c:
            c = Customer(woo_id=data["woo_id"]); self.db.add(c)
        c.email = data.get("email", c.email)
        c.name = data.get("name", c.name)
        c.orders_count = data.get("orders_count", c.orders_count)
        c.total_spent = data.get("total_spent", c.total_spent)
        self.db.commit(); self.db.refresh(c)
        return c
    def list(self): return self.db.query(Customer).all()
    def get(self, woo_id):
        return self.db.query(Customer).filter(Customer.woo_id == woo_id).first()

class OrderRepo:
    def __init__(self, db: Session): self.db = db
    def upsert(self, data: dict):
        o = self.db.query(Order).filter(Order.woo_id == data["woo_id"]).first()
        if not o:
            o = Order(woo_id=data["woo_id"]); self.db.add(o)
        o.customer_woo_id = data.get("customer_woo_id", o.customer_woo_id)
        o.status = data.get("status", o.status)
        o.total = data.get("total", o.total)
        o.currency = data.get("currency", o.currency)
        self.db.commit(); self.db.refresh(o)
        return o
    def list(self, status=None):
        q = self.db.query(Order)
        if status: q = q.filter(Order.status == status)
        return q.all()
    def get(self, woo_id):
        return self.db.query(Order).filter(Order.woo_id == woo_id).first()

class MessageRepo:
    def __init__(self, db: Session): self.db = db
    def create(self, data: dict):
        m = Message(**data); self.db.add(m); self.db.commit(); self.db.refresh(m); return m
    def list(self): return self.db.query(Message).all()
"repos"