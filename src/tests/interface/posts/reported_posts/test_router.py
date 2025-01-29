import uuid

from src.tests.test_client import client, setup_database
from src.tests.test_fixtures import (
    before_admin_login_cred,
    before_create_public_user_login_cred,
    before_create_private_user_login_cred,
    before_create_post,
    before_create_base_user,
    before_create_approved_follow_requests,
    before_create_normal_user,
    before_report_post
)
from src.tests.test_data import create_private_user, create_public_user
from src.tests.test_utils import create_session, get_auth_header, get_user_by_token
from lib.fastapi.custom_enums import ReportReason
from src.application.users.services import JWTService
from src.domain.models import User


def test_report_post(before_create_private_user_login_cred, before_create_post):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_public_user())
    response = client.post(
        f"/report-post/{post.id}/",
        json={
            "reason": ReportReason.COPYRIGHT.value,
            "additional_text": "additional text",
        },
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 200
    session.refresh(post)
    assert len(post.report) == 1
    session.close()


def test_report_post_already_reported_by_user(
    before_create_private_user_login_cred, before_report_post
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    report = before_report_post(
        session=session,
        posted_by=create_public_user(),
        reported_by={
            "username": user.username,
            "bio": user.bio,
            "profile_type": user.profile_type,
        },
    )
    response = client.post(
        f"/report-post/{report.post.id}/",
        json={
            "reason": ReportReason.HARASSMENT.value,
            "additional_text": "additional text",
        },
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 409
    session.close()


def test_report_post_by_admin(before_admin_login_cred):
    session = create_session()
    token = before_admin_login_cred(session=session)
    response = client.post(
        f"/report-post/{uuid.uuid4()}/",
        json={
            "reason": ReportReason.HARASSMENT.value,
            "additional_text": "additional text",
        },
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 403
    session.close()


def test_report_post_not_found(before_create_private_user_login_cred):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    response = client.post(
        f"/report-post/{uuid.uuid4()}/",
        json={
            "reason": ReportReason.COPYRIGHT.value,
            "additional_text": "additional text",
        },
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 200
    session.close()


def test_report_post_with_unauthorized_access():
    response = client.post(
        f"/report-post/{uuid.uuid4()}/",
        json={
            "reason": ReportReason.COPYRIGHT.value,
            "additional_text": "additional text",
        },
    )
    assert response.status_code == 401


def test_report_post_of_private_user_not_followed(
    before_create_private_user_login_cred, before_create_post
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    post = before_create_post(session=session, user_dict=create_private_user())
    response = client.post(
        f"/report-post/{post.id}/",
        json={
            "reason": ReportReason.COPYRIGHT.value,
            "additional_text": "additional text",
        },
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 403


def test_report_post_of_private_user_followed(
    before_create_private_user_login_cred,
    before_create_post,
    before_create_approved_follow_requests,
):
    session = create_session()
    token = before_create_private_user_login_cred(session=session)
    user = get_user_by_token(session=session, token=token)
    post = before_create_post(session=session, user_dict=create_private_user())
    before_create_approved_follow_requests(session=session, follower_id=user.id, following_id=post.posted_by)
    response = client.post(
        f"/report-post/{post.id}/",
        json={
            "reason": ReportReason.COPYRIGHT.value,
            "additional_text": "additional text",
        },
        headers=get_auth_header(token=token),
    )
    assert response.status_code == 200
    session.refresh(post)
    assert len(post.report) == 1
    session.close()