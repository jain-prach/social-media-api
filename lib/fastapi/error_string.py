from typing import List

def get_user_not_found() -> str:
    return "User doesn't exist!"

def get_incorrect_password() -> str:
    return "Incorrect email or password!"

def get_invalid_token() -> str:
    return "Invalid Credentials!"

def get_invalid_otp() -> str:
    return "Invalid Otp!"

def get_expired_otp() -> str:
    return "Otp expired! Generate new otp!"

def get_git_email_not_found() -> str:
    return "User email not found in git account"

def get_incorrect_id() -> str:
    return "Please provide a correct id value."

def get_no_permission() -> str:
    return "You don't have permission!"

def get_invalid_file_type(valid_types:List[str]):
    return f"Invalid File Type. Accepted valid types: {valid_types}"

def get_user_created() -> str:
    return "User already created! Do you want to update?"

def get_user_not_created() -> str:
    return "You have not created a user yet!"

def get_admin_not_created() -> str:
    return "You have not created an admin yet!"

def get_admin_to_not_create_user() -> str:
    return "Admin user can't create a user"