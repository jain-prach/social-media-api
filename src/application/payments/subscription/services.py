import uuid

from sqlmodel import Session

from src.domain.models import User, Subscription
from src.domain.payments.subscription.services import SubscriptionService
from src.application.payments.transaction.services import TransactionAppService
from src.application.users.users.services import UserAppService
from src.interface.payments.transaction.schemas import TransactionSchema
from src.interface.payments.subscription.schemas import SubscriptionSchema
from lib.fastapi.custom_enums import (
    SubscriptionInterval,
    ServiceModel,
    TransactionStatus,
)
from lib.fastapi.utils import (
    get_payment_interval,
    get_price,
    check_id,
)
from lib.fastapi.custom_exceptions import BadRequestException
from lib.fastapi.error_string import get_subscription_already_created, get_user_not_subscribed
from src.infrastructure.payment_service.services import StripeService
from src.setup.config.settings import settings


class SubscriptionAppService:
    """subscription application service for performing subscription tasks"""

    def __init__(self, session: Session):
        self.db_session = session
        self.subscription_service = SubscriptionService(session=session)

    def get_subscription_by_user_id(self, user_id: uuid.UUID):
        """get subscription by user id"""
        return self.subscription_service.get_subscription_by_user_id(user_id=user_id)

    def create_subscription(self, subscription: SubscriptionSchema) -> Subscription:
        """create subscription instance"""
        self.subscription_service.create(subscription=subscription)

    @staticmethod
    def create_checkout_for_subscription(
        subscription: SubscriptionInterval, user: User
    ):
        """create checkout for the user"""
        price = get_price(subscription=subscription)
        payment_interval = get_payment_interval(subscription=subscription)
        metadata = {"user_id": user.id, "interval": subscription}
        checkout = StripeService().create_subscription_checkout(
            price=price,
            payment_interval=payment_interval,
            product_name=settings.STRIPE_PRODUCT_NAME,
            metadata=metadata,
            email=user.base_user.email
        )
        return checkout

    def process_checkout(self, user_id: uuid.UUID, subscription: SubscriptionInterval):
        """processing checkout information"""
        user_app_service = UserAppService(session=self.db_session)
        user = user_app_service.get_user_by_base_user_id(base_user_id=user_id)
        if user.subscription:
            raise BadRequestException(get_subscription_already_created())
        checkout = self.create_checkout_for_subscription(
            subscription=subscription, user=user
        )
        transaction_app_service = TransactionAppService(session=self.db_session)
        transaction = TransactionSchema(
            payment_id=checkout["id"],
            user_id=check_id(id=checkout["metadata"]["user_id"]),
            amount=checkout["amount_total"] / 100,
            service_type=ServiceModel.SUBSCRIPTION,
            status=TransactionStatus.PROCESSING,
        )
        transaction_app_service.create_transaction(transaction=transaction)
        return checkout

    def complete_checkout(self, payload: bytes, stripe_signature: str) -> Subscription:
        """complete checkout when done"""
        event = StripeService.create_webhook_event(payload, stripe_signature)
        checkout_session = event.data.object
        user_id = check_id(checkout_session["metadata"]["user_id"])
        interval = checkout_session["metadata"]["interval"]
        transaction_app_service = TransactionAppService(session=self.db_session)
        db_transaction = transaction_app_service.update_transaction_status(
            payment_id=checkout_session["id"]
        )
        subscription = SubscriptionSchema(
            transaction_id=db_transaction.id, user_id=user_id, interval=interval
        )
        return self.create_subscription(subscription=subscription)

    def check_if_user_paid(self, user:User) -> None:
        """check whether the user is subscribed"""
        db_subscription = self.subscription_service.get_subscription_by_user_id(user_id=user.id)
        if not db_subscription:
            raise BadRequestException(get_user_not_subscribed())
        if db_subscription and db_subscription.is_cancelled:
            raise BadRequestException(get_user_not_subscribed())
        return None
