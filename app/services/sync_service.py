from ..repositories.repos import CustomerRepo, OrderRepo
from ..adapters.woocommerce import map_customer, map_order
from ..services.workflow_service import WorkflowService
from ..agents.crm_agent import CRMAgent

def sync_event(db, topic: str, payload: dict):
    customers = CustomerRepo(db)
    orders = OrderRepo(db)
    wf = WorkflowService(db)
    if "customer" in topic:
        data = map_customer(payload)
        customers.upsert(data)
        return {"entity": "customer", "woo_id": data["woo_id"]}
    if "order" in topic:
        data = map_order(payload)
        existing = orders.get(data["woo_id"])
        old_status = existing.status if existing else None
        order = orders.upsert(data)
        customer = customers.get(data["customer_woo_id"]) if data.get("customer_woo_id") else None
        # attempt fetch customer from payload nested
        if customer is None and payload.get("billing"):
            customer = customers.upsert(map_customer({"id": data["customer_woo_id"] or 0, "billing": payload.get("billing")}))
        agent = CRMAgent(db)
        msg = agent.handle_order_event(order, customer, old_status)
        return {"entity": "order", "woo_id": data["woo_id"], "message_id": getattr(msg, "id", None)}
    return {"entity": "unknown"}
"syn"