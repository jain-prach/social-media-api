import uuid
from typing import Optional

from sqlmodel import Session, select

from src.domain.models import Transaction
from lib.fastapi.utils import db_session_value_create
from src.interface.payments.transaction.schemas import TransactionSchema


class TransactionService:
    """services for handling Transaction database operations"""

    def __init__(self, session: Session):
        self.db_session = session

    def get_transaction_by_id(self, id: uuid.UUID) -> Optional[Transaction]:
        """get transaction by id from the database"""
        return self.db_session.get(Transaction, id)

    def get_transaction_by_user_id(self, user_id: uuid.UUID) -> Optional[Transaction]:
        """get transaction by user_id from the database"""
        return self.db_session.scalars(
            select(Transaction).where(Transaction.user_id == user_id)
        ).first()

    def get_transaction_by_payment_id(self, payment_id: str) -> Optional[Transaction]:
        return self.db_session.scalars(
            select(Transaction).where(Transaction.payment_id == payment_id)
        ).first()

    def create(self, transaction: TransactionSchema) -> Transaction:
        """create transaction instance in the database"""
        db_transaction = Transaction.model_validate(transaction)
        db_session_value_create(session=self.db_session, value=db_transaction)
        return db_transaction

    def update(
        self, transaction: TransactionSchema, db_transaction: Transaction
    ) -> Transaction:
        """update transaction in the database"""
        db_transaction.sqlmodel_update(transaction)
        db_session_value_create(session=self.db_session, value=db_transaction)
        return db_transaction

    def delete(self, db_transaction: Transaction) -> None:
        """delete transaction from the database"""
        self.db_session.delete(db_transaction)
        self.db_session.commit()
