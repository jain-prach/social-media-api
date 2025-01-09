import requests

from src.setup.config.settings import settings


class GithubOauthService:
    """authentication using github"""

    def __new__(cls):
        if not settings.GIT_CLIENT_SECRET:
            raise Exception("Error: Git client secret not found")
        if not settings.GIT_CLIENT_ID:
            raise Exception("Error: Git client id not found")
        if not hasattr(cls, "instance"):
            cls.instance = super(GithubOauthService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._client_id = settings.GIT_CLIENT_ID
        self._client_secret = settings.GIT_CLIENT_SECRET
        self._callback_url = settings.GIT_REDIRECT_URI

    def get_auth_url(self) -> str:
        """return git authentication url to receive code"""
        return f"https://github.com/login/oauth/authorize?client_id={self._client_id}&redirect_uri={self._callback_url}&scope=user:email"

    def get_access_token(self, code:str):
        """get access token from code to use for authorization to get user data"""
        # Token endpoint
        token_url = settings.GIT_TOKEN_URL

        # Request payload
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": self._callback_url,
        }

        # Set headers to request JSON response
        headers = {"Accept": "application/json"}

        response = requests.post(token_url, json=payload, headers=headers)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            return access_token
        return None

    def get_user_email(self, access_token:str):
        """get user email from github using the access_token generated during authentication"""
        api_url = settings.GIT_API_URL

        # Set headers with the access token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }

        # Make the GET request
        response = requests.get(api_url, headers=headers)
        user_email = response.json()[0].get("email")
        if response.status_code == 200:
            return user_email
        return None
