import json, os
from app.adapters.woocommerce import verify_signature, map_customer, map_order
from tests.conftest import sign

def test_sig_valid():
    b=b'{"id":1}'
    assert verify_signature(b, sign(b))

def test_sig_invalid():
    assert not verify_signature(b'{}', "bad")

def test_map_customer():
    d=map_customer({"id":5,"billing":{"email":"a@b.com","first_name":"A","last_name":"B"},"orders_count":2,"total_spent":"10"})
    assert d["woo_id"]==5 and d["email"]=="a@b.com"

def test_map_order():
    d=map_order({"id":7,"customer_id":5,"status":"processing","total":"9","currency":"USD","billing":{"email":"a@b.com"}})
    assert d["woo_id"]==7 and d["status"]=="processing"