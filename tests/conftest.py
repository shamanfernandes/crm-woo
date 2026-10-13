import os, hmac, hashlib, base64
os.environ["DATABASE_URL"]="sqlite:///./test.db"
os.environ["WOOCOMMERCE_WEBHOOK_SECRET"]="dev-secret"

def sign(body):
    return base64.b64encode(hmac.new(b"dev-secret", body, hashlib.sha256).digest()).decode()