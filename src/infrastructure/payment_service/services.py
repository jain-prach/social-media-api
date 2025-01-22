import math
from typing import Optional

import stripe

from lib.fastapi.custom_exceptions import CustomException
from src.setup.config.settings import settings


class StripeService:
    """stripe service for payment method"""

    def __new__(cls):
        if not settings.STRIPE_API_KEY:
            raise Exception("Error: stripe api key not found")
        if not hasattr(cls, "instance"):
            cls.instance = super(StripeService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        stripe.api_key = settings.STRIPE_API_KEY

    def create_subscription_checkout(
        self,
        price: int,
        payment_interval: dict,
        product_name: str,
        metadata: dict,
        email: Optional[str],
    ):
        """customizable subscription form to collect payments"""
        try:
            return stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "unit_amount": math.ceil(price * 100),
                            "currency": "usd",
                            "product_data": {"name": product_name},
                            "recurring": {
                                "interval": payment_interval["interval"],
                                "interval_count": payment_interval["count"],
                            },
                        },
                        "quantity": 1,
                    }
                ],
                metadata=metadata,
                customer_email=email if email else None,
                mode="subscription",
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
        except stripe.CardError as e:
            raise CustomException(detail=f"Stripe Card Error: {e}")
        except stripe.StripeError as e:
            raise CustomException(detail=f"Stripe Error: {e}")

    def create_webhook_event(payload: bytes, stripe_signature: str):
        """create webhook event to catch the process when done"""
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET_CHECKOUT_SUCCESS
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
        return event
