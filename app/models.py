from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    woo_id = Column(Integer, unique=True, index=True)
    email = Column(String, index=True)
    name = Column(String)
    orders_count = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    woo_id = Column(Integer, unique=True, index=True)
    customer_woo_id = Column(Integer)
    status = Column(String)
    total = Column(Float)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    to_email = Column(String)
    subject = Column(String)
    body = Column(Text)
    status = Column(String, default="drafted")
    channel = Column(String, default="console")
    source = Column(String, default="rule-based")
    trace = Column(Text, default="[]")
    order_woo_id = Column(Integer)
"models"