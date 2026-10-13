import os
os.environ.setdefault("DATABASE_URL","sqlite:///./test.db")
from app.db import init_db, SessionLocal
from app.repositories.repos import CustomerRepo, OrderRepo, MessageRepo

def test_upsert_idempotent():
    from app.db import Base, engine
    Base.metadata.drop_all(engine)
    init_db()
    db=SessionLocal()
    try:
        r=CustomerRepo(db)
        r.upsert({"woo_id":1,"email":"a@b.com","name":"A","orders_count":1,"total_spent":10.0})
        r.upsert({"woo_id":1,"email":"a@b.com","name":"A","orders_count":2,"total_spent":20.0})
        assert len(r.list())==1
        assert r.get(1).orders_count==2
    finally:
        db.close()