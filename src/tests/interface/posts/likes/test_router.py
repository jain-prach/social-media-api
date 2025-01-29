import uuid

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import before_create_post, before_create_normal_user, before_create_base_user, before_create_private_user_login_cred
from src.tests.test_utils import create_session, get_auth_header
from src.tests.test_data import create_private_user, create_public_user
from src.domain.models import Post

def test_like_post(before_create_private_user_login_cred, before_create_post):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_public_user())
    response = client.get(f"/like/{post.id}", headers=get_auth_header(token=token))
    assert response.status_code == 200
    post_id = post.id
    session.close()
    session = create_session()
    db_post = session.get(Post, post_id)
    assert db_post.likes is not None
    assert len(db_post.likes) == 1
    session.close()

def test_like_post_with_unauthorized_access():
    response = client.get(f"/like/{uuid.uuid4()}")
    assert response.status_code == 401

def test_like_post_for_no_post_created(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.get(f"/like/{uuid.uuid4()}", headers=get_auth_header(token=token))
    assert response.status_code == 200