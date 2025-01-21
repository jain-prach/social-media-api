import math

import stripe
from src.setup.config.settings import settings
from lib.fastapi.custom_enums import PriceModel
from lib.fastapi.utils import get_payment_interval


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

    def create_subscription_checkout(self, price:PriceModel):
        """customizable subscription form to collect payments"""
        payment_interval = get_payment_interval(price=price)
        return stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "unit_amount": math.ceil(price.value * 100),
                        "currency": "usd",
                        "product_data": {"name": settings.STRIPE_PRODUCT_NAME},
                        "recurring": {
                            "interval": payment_interval["interval"],
                            "interval_count": payment_interval["count"],
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )
