from ..repositories.repos import CustomerRepo, OrderRepo, MessageRepo
from ..strategies.messaging import template_for, channel

class WorkflowService:
    def __init__(self, db):
        self.customers = CustomerRepo(db)
        self.orders = OrderRepo(db)
        self.messages = MessageRepo(db)
    def on_order_status(self, order, customer):
        # decides message based on status; returns Message or None
        if order.status not in ("confirmed","processing","shipped","completed"):
            return None
        tmpl = template_for(order.status)
        body = tmpl.render(order.status, customer, order)
        ch = channel()
        status = ch.send(customer.email, f"Order #{order.woo_id} {order.status}", body)
        return self.messages.create({
            "to_email": customer.email,
            "subject": f"Order #{order.woo_id} {order.status}",
            "body": body,
            "status": status,
            "channel": ch.name,
            "order_woo_id": order.woo_id,
        })
"workflow"