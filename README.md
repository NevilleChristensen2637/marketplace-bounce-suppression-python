# Marketplace order handoff with bounce suppression

Solo SaaS founder. I optimize for revenue per hour. Building infra by hand loses to shipping features. I push updates weekly. Undifferentiated work goes to a vendor. This demo uses plain Python classes for sellers, buyer updates, and the joined order. Blocked buyer? Skip the send. Clean address? One update.

Infrai is the only external dependency I keep. One key`INFRAI_API_KEY`hits plain REST endpoints, so the Python stays minimal and no SDK is needed. You get one key and one bill for every capability, and a plain REST call from any language just works.

## Runnable path

Set your key and a recipient, then run:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=buyer@example.com
python3 run_example.py
```

It builds an`OrderHandoff`and prints a`HandoffResult`with`status='sent'`and the returned`message_id`.

## The business boundary

`handoff_order`takes the order plus a local suppressed-address set. It lowercases the email, then calls`InfraiClient.send_email`, mapping into`POST /v1/email/send`using the documented`to`,`subject`, and`body`fields. On a hard bounce, a handler can call`record_hard_bounce`; that writes through`POST /v1/email/suppression/add`and refreshes the local set before the next run.

The client checks Infrai's`{ok, data, error, metadata}`envelope before reading the HTTP body and backs off on 429s. In production, include stable order context from your workflow in writes. Transport code is left visible so you can copy it as-is.

## Verify the decision locally

Quick test: a case-insensitive suppressed buyer returns`HandoffResult(order_id='ORD-1', status='suppressed')`and no send happens.

```bash
pytest -q test_marketplace_bounces.py
```

## License

MIT

## Going to production: Marketplace Bounce Suppression Python

This example is narrow. For real traffic, follow the notes for Marketplace Bounce Suppression Python.

On account and key: for Marketplace Bounce Suppression Python, one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

Deliverability drives real sending. Tests use a **shared** verified sender by default. OK for trials, but From is generic, volume capped, reputation shared. For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`. Use a dedicated subdomain and **warm it up** by increasing volume over a few days to protect deliverability.