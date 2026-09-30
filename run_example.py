import os

from marketplace_bounces import BuyerUpdate, InfraiClient, OrderHandoff, SellerAsset, handoff_order


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("Set DEMO_EMAIL_TO together with INFRAI_API_KEY")
    order = OrderHandoff("ORD-1042", SellerAsset("SKU-7", "Handmade lamp"), BuyerUpdate(recipient, "Your seller has handed off the package."))
    result = handoff_order(order, set(), InfraiClient())
    print(result)


if __name__ == "__main__":
    main()

