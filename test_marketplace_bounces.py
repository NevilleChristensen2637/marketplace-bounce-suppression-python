from marketplace_bounces import BuyerUpdate, InfraiClient, OrderHandoff, SellerAsset, HandoffResult, handoff_order


class FakeClient:
    def send_email(self, to, subject, text):
        raise AssertionError("suppressed buyers must not receive a send request")


def test_handoff_skips_suppressed_buyer():
    order = OrderHandoff("ORD-1", SellerAsset("A-1", "Ceramic mug"), BuyerUpdate("Buyer@Example.com", "handoff"))
    result = handoff_order(order, {"buyer@example.com"}, FakeClient())
    assert result == HandoffResult("ORD-1", "suppressed")


def test_send_email_uses_documented_body_field(monkeypatch):
    calls = []
    monkeypatch.setattr(InfraiClient, "_call", lambda self, method, path, payload: calls.append((method, path, payload)) or {})
    InfraiClient("test-key").send_email("chenhua@changba.com", "Order update", "Ready")
    assert calls == [("POST", "/v1/email/send", {"to": "chenhua@changba.com", "subject": "Order update", "body": "Ready"})]
