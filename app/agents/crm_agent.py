import json
from ..repositories.repos import MessageRepo, CustomerRepo, OrderRepo
from ..strategies.messaging import template_for, channel
from .llm_client import LLMClient, LLMError

TOOLS=[{"type":"function","function":{"name":"get_customer","description":"Get customer by woo id","parameters":{"type":"object","properties":{"woo_id":{"type":"integer"}},"required":["woo_id"]}}},
 {"type":"function","function":{"name":"list_orders","description":"List orders by status","parameters":{"type":"object","properties":{"status":{"type":"string"}}}}},
 {"type":"function","function":{"name":"draft_message","description":"Draft message","parameters":{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}},"required":["to","subject","body"]}}},
 {"type":"function","function":{"name":"send_message","description":"Send drafted message","parameters":{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}},"required":["to","subject","body"]}}}]

class CRMAgent:
    def __init__(self, db, llm=None):
        self.db=db
        self.messages=MessageRepo(db)
        self.customers=CustomerRepo(db)
        self.orders=OrderRepo(db)
        self.llm=llm or LLMClient()

    def _rule(self, order, customer):
        if order.status not in ("confirmed","processing","shipped","completed"): return None
        base=template_for(order.status).render(order.status, customer, order)
        if customer and (customer.orders_count or 0)>1: base+=" Thanks for being a repeat customer!"
        if customer and float(customer.total_spent or 0)>500: base+=" VIP appreciation."
        return base, "rule-based", []

    def handle_order_event(self, order, customer, old_status):
        if old_status and old_status==order.status:
            return None
        trace=[]
        source="rule-based"
        body=None
        reasoning=""
        if self.llm.available():
            try:
                system="You are a CRM agent. Use tools to personalise a message."
                messages=[{"role":"system","content":system},
                          {"role":"user","content":f"Order {order.woo_id} status={order.status} customer_id={getattr(customer,'woo_id',None)} repeat={(customer.orders_count or 0)>1 if customer else False} spent={getattr(customer,'total_spent',0)}"}]
                for _ in range(4):
                    res=self.llm.chat(messages, TOOLS)
                    trace.append({"content":res["content"],"reasoning":res["reasoning"],"tool_calls":res["tool_calls"]})
                    reasoning=res["reasoning"] or reasoning
                    if not res["tool_calls"]:
                        body=res["content"]; source="llm"; break
                    for tc in res["tool_calls"]:
                        name=tc["function"]["name"]
                        try:
                            args=json.loads(tc["function"].get("arguments","{}"))
                        except json.JSONDecodeError:
                            args={}
                            trace.append({"tool":name,"error":"bad args"})
                            continue
                        result=self._tool(name,args,order,customer)
                        trace.append({"tool":name,"args":args,"result":result})
                        messages.append({"role":"assistant","content":"","tool_calls":[tc]})
                        messages.append({"role":"tool","tool_call_id":tc.get("id",""),"content":json.dumps(result)})
            except LLMError:
                body=None
        if not body:
            rb,source,rt=self._rule(order,customer)
            if rb is None: return None
            body=rb
            trace = trace + rt
            source="rule-based"
        if not body or order.status not in ("confirmed","processing","shipped","completed"):
            # still allow if llm produced
            if order.status not in ("confirmed","processing","shipped","completed") and source=="rule-based":
                return None
        # if llm body but status not standard, still send? require content
        ch=channel()
        delivery=ch.send(customer.email if customer else "", f"Order #{order.woo_id} {order.status}", body)
        return self.messages.create({
            "to_email": customer.email if customer else "",
            "subject": f"Order #{order.woo_id} {order.status}",
            "body": body,
            "status": delivery,
            "channel": ch.name,
            "source": source,
            "trace": json.dumps(trace),
            "order_woo_id": order.woo_id,
        })

    def _tool(self, name, args, order, customer):
        if name=="get_customer":
            c=self.customers.get(args.get("woo_id") or getattr(customer,"woo_id",None))
            return {"woo_id":getattr(c,"woo_id",None),"name":getattr(c,"name",None),"orders_count":getattr(c,"orders_count",None),"total_spent":getattr(c,"total_spent",None)} if c else None
        if name=="list_orders":
            return [{"woo_id":o.woo_id,"status":o.status,"total":o.total} for o in self.orders.list(args.get("status"))]
        if name in ("draft_message","send_message"):
            return {"ok": True}
        return {"error":"unknown tool"}