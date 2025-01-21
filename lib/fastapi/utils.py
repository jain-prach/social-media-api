import pytz
import random
import uuid
from typing import List
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlmodel import Session

from lib.fastapi.custom_enums import Role, FilterDates, SubscriptionInterval, PriceModel
from lib.fastapi.custom_exceptions import CustomValidationError, ForbiddenException
from lib.fastapi.error_string import (
    get_incorrect_id,
    get_no_permission,
    get_invalid_file_type,
    get_admin_not_allowed,
)
from src.setup.config.settings import settings


def get_default_timezone():
    """get tz value for str timezone"""
    return pytz.timezone(settings.TIMEZONE)


def generate_otp():
    """returns a random 6 digit otp"""
    return random.randrange(100000, 999999)


def check_id(id: str) -> uuid.UUID:
    try:
        return uuid.UUID(id)
    except ValueError:
        raise CustomValidationError(get_incorrect_id())


def db_session_value_create(session: Session, value: dict):
    """helper function for repetitive database operation"""
    session.add(value)
    session.commit()
    session.refresh(value)


def get_valid_image_formats_list() -> List[str]:
    return ["image/jpeg", "image/png", "image/heic", "image/jpg"]

def get_valid_post_formats_list() -> List[str]:
    return ["image/jpeg", "image/png", "image/heic", "image/jpg", "video/mp4", "video/mpeg"]

def only_admin_access(current_user: dict) -> None:
    """only admin users can have access"""
    if current_user.get("role") == Role.USER.value:
        raise ForbiddenException(get_no_permission())

def only_user_access(current_user:dict) -> None:
    """only normal users can have access"""
    if current_user.get("role") == Role.ADMIN.value:
        raise ForbiddenException(get_admin_not_allowed())

def only_own_access(current_user: dict, access_id: uuid.UUID) -> None:
    """only own details access"""
    if uuid.UUID(current_user.get("id")) != access_id:
        raise ForbiddenException(get_no_permission())
    return None


def check_file_type(content_type: str, valid_types: List) -> None:
    if content_type not in valid_types:
        raise CustomValidationError(
            get_invalid_file_type(valid_types=valid_types)
        )

def get_after_date_from_enum(value:FilterDates) -> datetime:
    """get date value from today based on enum"""
    today = datetime.now(tz=get_default_timezone())
    if value == FilterDates.THIS_MONTH.value:
        delta = relativedelta(months=1)
    elif value == FilterDates.LAST_SIX_MONTHS.value:
        delta = relativedelta(months=6)
    elif value == FilterDates.LAST_ONE_YEAR.value:
        delta = relativedelta(years=1)
    else:
        delta = relativedelta(years=10)
    return today-delta

def get_unique_constraint_error(error_message:str) -> str:
    """formatting unique constraint error"""
    error_pattern = r"Key \((.+)\)=\((.+?)\)"
    match = re.search(error_pattern, error_message)
    if match:
        column_name = match.group(1)  # Extracts 'object'
        column_value = match.group(2)  # Extracts 'value'
        return "{} {} already exists.".format(column_name.capitalize(), column_value)
    
def get_pydantic_validation_error(errors:List) -> List:
    """formatting pydantic validation error"""
    error_output = []
    for error in errors:
        error_dict = {"loc":error["loc"], "msg":error["msg"], "type":error["type"]}
        error_output.append(error_dict)
    return error_output

def get_random_values_from_list(var_list:List, count:int) -> List:
    """
    select random values from a list
    `Args`
        var_list:
            list to select random values from
        count:
            number of values to select
    `Returns`
        [List]:
            selected random values
    """
    if len(var_list) < count:
        return var_list
    return random.choices(population=var_list, k=count)

def get_price(subscription:SubscriptionInterval) -> int:
    """get price based on interval"""
    if subscription == SubscriptionInterval.DAILY:
        price = PriceModel.DAILY
    elif subscription == SubscriptionInterval.MONTHLY:
        price = PriceModel.MONTHLY
    else:
        price = PriceModel.YEARLY
    return price

def get_payment_interval(price:PriceModel) -> dict:
    """get payment interval using price"""
    if price == PriceModel.DAILY:
        interval = {"interval": "day", "count": 1}
    elif price == PriceModel.MONTHLY:
        interval = {"interval": "month", "count": 1}
    else:
        interval = {"interval":"year", "count": 1}
    return interval