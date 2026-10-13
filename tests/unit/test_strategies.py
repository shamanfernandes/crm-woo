from app.strategies.messaging import template_for, factory
def test_templates():
    for s in ["confirmed","processing","shipped","completed"]:
        t=template_for(s)
        class O: woo_id=1; total=5; currency="USD"
        class C: name="X"
        out=t.render(s,C(),O())
        assert "order #1" in out.lower() or "order" in out.lower()