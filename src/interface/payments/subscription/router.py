from fastapi import APIRouter, Request, Header
from starlette.status import HTTP_200_OK

from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from .schemas import (
    PaymentSuccessResponseData,
    PaymentCancelResponseData,
    SubscriptionResponseData,
)
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.custom_enums import SubscriptionInterval
from src.application.payments.subscription.services import (
    SubscriptionAppService,
)
from lib.fastapi.utils import check_id

router = APIRouter(
    prefix="/payment", tags=["payments"], route_class=UniqueConstraintErrorRoute
)


@router.get("/subscribe/", status_code=HTTP_200_OK)
def subscribe(
    current_user: AuthDep, subscription: SubscriptionInterval, session: SessionDep
):
    """to subscribe to access paid services"""
    subscription_app_service = SubscriptionAppService(session=session)
    checkout = subscription_app_service.process_checkout(
        user_id=check_id(id=current_user.get("id")), subscription=subscription
    )
    return {"message": "Checkout", "success": True, "data": {"url": checkout.url}}


@router.get(
    "/success/", status_code=HTTP_200_OK, response_model=PaymentSuccessResponseData
)
def success():
    """payment successful endpoint"""
    return {}


@router.get(
    "/cancel/", status_code=HTTP_200_OK, response_model=PaymentCancelResponseData
)
def cancel():
    """payment cancelled endpoint"""
    return {}


# @router.get("/")
# def test(payment_id: str, session: SessionDep):
#     transaction = TransactionAppService(session=session).update_transaction_status(
#         payment_id=payment_id
#     )
#     subscription = SubscriptionAppService(session=session).create_subscription(
#         SubscriptionSchema(
#             transaction_id=transaction.id,
#             user_id=transaction.user_id,
#             interval=SubscriptionInterval.MONTHLY,
#         )
#     )
#     return transaction.model_dump()


@router.post("/webhook/checkout/success/", response_model=SubscriptionResponseData)
async def checkout_success(
    request: Request, session: SessionDep, stripe_signature: str = Header(None)
):
    """webhook endpoint for `checkout.session.completed` event"""

    payload = await request.body()
    subscription_app_service = SubscriptionAppService(session=session)
    db_subscription = subscription_app_service.complete_checkout(
        payload=payload, stripe_signature=stripe_signature
    )
    return {"data": db_subscription}
