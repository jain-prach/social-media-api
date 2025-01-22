import uuid
from typing import Optional

from sqlmodel import Session

from src.domain.models import Transaction
from src.domain.payments.transaction.services import TransactionService
from src.interface.payments.transaction.schemas import TransactionSchema
from lib.fastapi.custom_enums import TransactionStatus
from lib.fastapi.custom_exceptions import BadRequestException
from lib.fastapi.error_string import get_transaction_not_created

class TransactionAppService:
    """transaction application service for handling transactions"""

    def __init__(self, session:Session):
        self.db_session = session
        self.transaction_service = TransactionService(session=session)

    def get_transaction_by_id(self, id: uuid.UUID) -> Optional[Transaction]:
        """get transaction by id"""
        return self.transaction_service.get_transaction_by_id(id=id)
    
    def get_transaction_by_user_id(self, user_id:uuid.UUID) -> Optional[Transaction]:
        """get transaction by user id"""
        return self.transaction_service.get_transaction_by_user_id(user_id=user_id)
    
    def get_transaction_by_payment_id(self, payment_id:str) -> Optional[Transaction]:
        """get transaction by payment id"""
        return self.transaction_service.get_transaction_by_payment_id(payment_id=payment_id)
    
    def create_transaction(self, transaction:TransactionSchema) -> Transaction:
        """create transaction"""
        return self.transaction_service.create(transaction=transaction)
    
    def update_transaction_status(self, payment_id:str) -> Transaction:
        """update transaction status to completed"""
        db_transaction = self.get_transaction_by_payment_id(payment_id=payment_id)
        if db_transaction:
            transaction=TransactionSchema(**db_transaction.model_dump())
            transaction.status = TransactionStatus.COMPLETED
            return self.transaction_service.update(transaction=transaction, db_transaction=db_transaction)
        else:
            raise BadRequestException(detail=get_transaction_not_created())
