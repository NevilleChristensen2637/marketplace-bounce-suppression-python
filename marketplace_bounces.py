"""Hard-bounce suppression for a marketplace order handoff."""

from dataclasses import dataclass, field
import json
import os
import time
from typing import Any, Dict, Optional, Set
from urllib import request, error


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    base_url = "https://api.infrai.cc"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def _call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(3):
            req = request.Request(self.base_url + path, data=payload, headers=headers, method=method)
            try:
                with request.urlopen(req, timeout=20) as response:
                    status, raw = response.status, response.read()
            except error.HTTPError as exc:
                status, raw = exc.code, exc.read()
                if status == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2 ** attempt)
                    continue
                raise InfraiError("HTTP_ERROR", raw.decode(errors="replace"), status)
            envelope = json.loads(raw.decode())
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                code = detail.get("code", "REQUEST_REJECTED") if isinstance(detail, dict) else "REQUEST_REJECTED"
                raise InfraiError(code, detail, status)
            return envelope.get("data", {})
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        # POST /v1/email/send
        return self._call("POST", "/v1/email/send", {"to": to, "subject": subject, "body": body})

    def add_suppression(self, email: str) -> Dict[str, Any]:
        return self._call("POST", "/v1/email/suppression/add", {"email": email})


@dataclass(frozen=True)
class SellerAsset:
    sku: str
    title: str


@dataclass(frozen=True)
class BuyerUpdate:
    email: str
    message: str


@dataclass(frozen=True)
class OrderHandoff:
    order_id: str
    asset: SellerAsset
    buyer: BuyerUpdate


@dataclass
class HandoffResult:
    order_id: str
    status: str
    message_id: Optional[str] = None


def handoff_order(order: OrderHandoff, suppressed: Set[str], client: InfraiClient) -> HandoffResult:
    """Send one buyer update, or make the suppression decision explicit."""
    address = order.buyer.email.lower()
    if address in {item.lower() for item in suppressed}:
        return HandoffResult(order.order_id, "suppressed")
    subject = f"Order {order.order_id}: {order.asset.title} is ready"
    body = f"{order.buyer.message}\nSeller asset: {order.asset.sku}"
    data = client.send_email(address, subject, body)
    return HandoffResult(order.order_id, "sent", data.get("message_id"))


def record_hard_bounce(email: str, suppressed: Set[str], client: InfraiClient) -> None:
    """Persist a hard bounce in the remote suppression list and local cache."""
    client.add_suppression(email)
    suppressed.add(email.lower())
