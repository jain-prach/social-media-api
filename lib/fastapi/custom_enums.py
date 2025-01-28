from enum import Enum


class Role(str, Enum):
    """enum for role: user and admin"""
    USER = "user"
    ADMIN = "admin"


class ProfileType(str, Enum):
    """enum for profile type: public and private"""
    PUBLIC = "public"
    PRIVATE = "private"

class StatusType(str, Enum):
    """enum for status type: pending, accepted, rejected"""
    PENDING = "pending"
    # ACCEPTED = "accepted"
    APPROVED = "approved"
    REJECTED = "rejected"

class FilterDates(str, Enum):
    """enum for filtering by dates"""
    THIS_MONTH = "this-month"
    LAST_SIX_MONTHS = "last-6-months"
    LAST_ONE_YEAR = "last-1-year"
    LAST_TEN_YEARS = "last-10-years"

class ReportReason(str, Enum):
    """enum for selecting reporting reason"""
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    HARASSMENT = "harassment"
    COPYRIGHT = "copyright"
    OTHER = "other"

class ServiceModel(str, Enum):
    SUBSCRIPTION = "subscription"
    PRODUCT = "product"

class TransactionStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"

class SubscriptionInterval(str, Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    DAILY = "daily"

class PriceModel(int, Enum):
    YEARLY = 400
    MONTHLY = 100
    DAILY = 20

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"