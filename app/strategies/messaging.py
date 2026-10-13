from ..config import SMTP_ENABLED

class TemplateStrategy:
    def render(self, status, customer, order): raise NotImplementedError

class ConfirmedTemplate(TemplateStrategy):
    def render(self, status, customer, order):
        return f"Hi {customer.name or 'there'}, your order #{order.woo_id} is confirmed. Total {order.currency} {order.total}."

class ShippedTemplate(TemplateStrategy):
    def render(self, status, customer, order):
        return f"Hi {customer.name or 'there'}, order #{order.woo_id} has shipped!"

class CompletedTemplate(TemplateStrategy):
    def render(self, status, customer, order):
        return f"Hi {customer.name or 'there'}, order #{order.woo_id} delivered. Thanks!"

class DefaultTemplate(TemplateStrategy):
    def render(self, status, customer, order):
        return f"Update on order #{order.woo_id}: {status}"

TEMPLATES = {"confirmed": ConfirmedTemplate, "processing": ConfirmedTemplate,
             "shipped": ShippedTemplate, "completed": CompletedTemplate}

def template_for(status):
    cls = TEMPLATES.get(status, DefaultTemplate)
    return cls()

class Channel:
    name = "base"
    def send(self, to, subject, body): raise NotImplementedError

class ConsoleChannel(Channel):
    name = "console"
    def send(self, to, subject, body):
        print(f"[EMAIL->console] to={to} subj={subject}\n{body}")
        return "sent"

class SmtpChannel(Channel):
    name = "smtp"
    def send(self, to, subject, body):
        if not SMTP_ENABLED: return "drafted"
        # real smtp omitted; channel simulates send
        return "sent"

def channel():
    return SmtpChannel() if SMTP_ENABLED else ConsoleChannel()

def factory(status):
    return template_for(status), channel()
"strategies"