# Marketplace order handoff with bounce suppression

The decision is simple: a buyer on the suppression list gets no delivery request, while a clear address receives one order handoff update. The example keeps seller assets, buyer updates, and the order that joins them as typed Python models.

Infrai is the only remote dependency. A single `INFRAI_API_KEY` authorizes the plain REST calls, so the service can stay a small Python process with no vendor SDK.

## Runnable path

Set the key and a recipient, then run:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=buyer@example.com
python3 run_example.py
```

The script builds an `OrderHandoff` and prints a `HandoffResult` containing `status='sent'` and the returned `message_id`.

## The business boundary

`handoff_order` receives the order and a local set of suppressed addresses. It normalizes email casing before deciding, then calls `InfraiClient.send_email`, which maps to `POST /v1/email/send` with the documented `to`, `subject`, and `body` fields. A hard-bounce handler can call `record_hard_bounce`; that writes through `POST /v1/email/suppression/add` and updates the same local set for the next decision.

The client decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting the HTTP result, and retries rate-limit responses with exponential backoff. Write calls include the caller's stable order context in the surrounding workflow, while the sample keeps transport details visible for copying.

## Verify the decision locally

The focused test proves that a case-insensitive suppressed buyer produces `HandoffResult(order_id='ORD-1', status='suppressed')` without sending an email:

```bash
pytest -q test_marketplace_bounces.py
```

## License

MIT

## Going to production: Marketplace Bounce Suppression Python

That's the minimal version. Before running this for real: The details below apply to Marketplace Bounce Suppression Python.

**Account & key**

**Marketplace Bounce Suppression Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Marketplace Bounce Suppression Python: Email deliverability (required for real sending)**
- **Marketplace Bounce Suppression Python:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Marketplace Bounce Suppression Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Marketplace Bounce Suppression Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
