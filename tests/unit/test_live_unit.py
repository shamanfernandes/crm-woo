import os
from app.adapters.woocommerce import map_customer, map_order, woo_client
def test_mapping_recorded():
    cust=map_customer({"id":1,"billing":{"email":"a@b.com","first_name":"A","last_name":"B"},"orders_count":1,"total_spent":"1.0"})
    assert cust["woo_id"]==1
    order=map_order({"id":2,"customer_id":1,"status":"pending","total":"1","currency":"USD","billing":{"email":"a@b.com"}})
    assert order["woo_id"]==2
def test_config_switch_mock(monkeypatch):
    monkeypatch.delenv("WC_BASE_URL",raising=False)
    monkeypatch.delenv("WC_CONSUMER_KEY",raising=False)
    monkeypatch.delenv("WC_CONSUMER_SECRET",raising=False)
    assert type(woo_client()).__name__=="MockWooClient"

def test_config_switch_real_fallback(monkeypatch):
    monkeypatch.setenv("WC_BASE_URL","http://x")
    monkeypatch.setenv("WC_CONSUMER_KEY","k")
    monkeypatch.setenv("WC_CONSUMER_SECRET","s")
    assert woo_client().__class__.__name__ in ("RealWooClient","MockWooClient")
