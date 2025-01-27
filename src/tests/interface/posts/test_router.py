from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_create_private_user_login_cred,
    before_create_public_user_login_cred,
    before_create_normal_user,
    before_create_post,
    before_create_base_user,
)
from src.tests.test_data import create_public_user, create_private_user
from src.tests.test_utils import create_session, get_auth_header

from src.domain.models import User


def test_list_posts_for_public_user(
    before_create_private_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_public_user())
    user = session.get(User, post.posted_by)
    session.close()
    response = client.get(f"/posts/{user.username}/", headers=get_auth_header(token))
    assert response.status_code == 200

def test_list_posts_for_private_user(
    before_create_public_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_private_user())
    user = session.get(User, post.posted_by)
    session.close()
    response = client.get(f"/posts/{user.username}/", headers=get_auth_header(token))
    assert response.status_code == 403

def test_create_post(before_create_public_user_login_cred):
    session = create_session()
    token = before_create_public_user_login_cred(session=session)
    session.close()
    with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
        response = client.post(
            "post/",
            headers=get_auth_header(token),
            files=[("media", f), ("media", f)],
        )
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data["media"]) == 2
