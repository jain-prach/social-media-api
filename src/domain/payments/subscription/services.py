import uuid
from typing import Optional

from sqlmodel import Session, select

from src.domain.models import Subscription
from src.interface.payments.subscription.schemas import SubscriptionSchema
from lib.fastapi.utils import db_session_value_create

class SubscriptionService:
    """services for handling subscription database operations"""

    def __init__(self, session:Session):
        self.db_session = session

    def get_subscription_by_id(self, id: uuid.UUID) -> Optional[Subscription]:
        """get subscription by id from the database"""
        return self.db_session.get(Subscription, id)

    def get_subscription_by_user_id(self, user_id: uuid.UUID) -> Optional[Subscription]:
        """get subscription by user_id from the database"""
        return self.db_session.scalars(
            select(Subscription).where(Subscription.user_id == user_id)
        ).first()

    # def get_subscription_by_user_id_with_access_time(self, user_id: uuid.UUID
    # ) -> Optional[Subscription]:
    #     """get subscription by user_id for access time that is left"""
    #     return self.db_session.scalars(
    #         select(Subscription)
    #         .where(Subscription.access_time >= datetime.now())
    #         .where(Subscription.user_id == user_id)
    #     ).first()
    
    def create(self, subscription:SubscriptionSchema) -> Subscription:
        """create subscription instance in the database"""
        db_subscription = Subscription.model_validate(subscription)
        db_session_value_create(session=self.db_session, value=db_subscription)
        return db_subscription

    def update(self, subscription: Subscription, db_subscription: Subscription) -> Subscription:
        """update subscription in the database"""
        db_subscription.sqlmodel_update(subscription)
        db_session_value_create(session=self.db_session, value=db_subscription)
        return db_subscription

    def delete(self, db_subscription: Subscription) -> None:
        """delete subscription from the database"""
        self.db_session.delete(db_subscription)
        self.db_session.commit()