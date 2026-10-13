import os
os.environ["DATABASE_URL"]="sqlite:///./sim.db"
os.environ["WOOCOMMERCE_WEBHOOK_SECRET"]="dev-secret"
os.environ["DEBUG"]="true"
from fastapi.testclient import TestClient
from app.db import Base, engine
from app.main import app
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
client=TestClient(app)
def test_simulate_on():
    r=client.post("/dev/simulate")
    assert r.status_code==200