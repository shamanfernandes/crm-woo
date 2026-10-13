import os, pytest
@pytest.mark.live
def test_live_import():
    if not (os.getenv("WC_BASE_URL") and os.getenv("WC_CONSUMER_KEY") and os.getenv("WC_CONSUMER_SECRET")):
        pytest.skip("live env not set")
    from app.adapters.woocommerce import woo_client
    c=woo_client()
    assert isinstance(c.list_customers(), list)
