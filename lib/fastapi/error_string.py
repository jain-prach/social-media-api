from typing import List


def get_user_not_found() -> str:
    return "User not found!"


def get_password_value_error() -> str:
    return "Min length(8) and Password must contain at least one lower character, one upper character, digit and special symbol"

def get_username_value_error() -> str:
    return "Min length(3), Max length(32), Username cannot include spaces and symbols other than . or _"


def get_incorrect_password() -> str:
    return "Incorrect email or password!"


def get_invalid_token() -> str:
    return "Invalid Credentials!"


def get_invalid_otp() -> str:
    return "Invalid Otp!"


def get_expired_otp() -> str:
    return "Otp expired! Generate new otp!"


def get_access_token_expired() -> str:
    return "Login token expired! Login again to continue."


def get_git_email_not_found() -> str:
    return "User email not found in git account"


def get_otp_link_expired() -> str:
    return "Otp link expired! Generate new."

def get_invalid_otp_token() -> str:
    return "Otp token invalid!"


def get_incorrect_id() -> str:
    return "Please provide a correct id value."


def get_no_permission() -> str:
    return "You don't have permission!"


def get_invalid_file_type(valid_types: List[str]):
    return f"Invalid File Type. Accepted valid types: {valid_types}"


def get_user_created() -> str:
    return "User already created! Do you want to update?"


def get_admin_created() -> str:
    return "Admin already created! Do you want to update?"


def get_user_not_created() -> str:
    return "You have not created a user yet!"


def get_admin_not_created() -> str:
    return "You have not created an admin yet!"


def get_admin_to_not_create_user() -> str:
    return "Admin user can't create a user"


def get_admin_not_allowed() -> str:
    return "Admin user can't perform this action"


def get_send_request_to_yourself() -> str:
    return "A user cannot follow themselves"

def get_request_already_sent() -> str:
    return "Request already sent!"


def get_post_not_found() -> str:
    return "Post not found!"

def get_post_already_liked() -> str:
    return "Post already liked!"

def get_post_reported_once() -> str:
    return "You have already reported the post! We will look into it and get back to you!"

def get_user_is_private() -> str:
    return "This is an private user. You must follow to access their contents."

def get_subscription_already_created() -> str:
    return "Subscription already exists, we suggest you to update!"

def get_transaction_not_created() -> str:
    return "Transaction not found!"

def get_user_not_subscribed() -> str:
    return "Please subscribe to access this url!"