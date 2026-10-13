docker compose up -d
Open http://localhost:8080/wp-admin (admin/admin123)
WooCommerce > Settings > Advanced > REST API add key
Webhooks: customer.created, order.created, order.updated to http://host.docker.internal:8000/webhook/woocommerce secret WC_WEBHOOK_SECRET
Place test order, verify dashboard.
