
from src.infrastructure.scheduler.celery import app
from src.application.users.services import UserAppService
from src.application.posts.services import PostAppService
from src.setup.config.database import get_session

@app.task
def schedule_post_notifications():
    """schedule post notifications celery task"""
    try:
        sessions = get_session()
        session = list(sessions)[0]
        user_app_service = UserAppService(session=session)
        users = user_app_service.get_all_users()
        post_app_service = PostAppService(session=session)
        for user in users:
            random_post_ids = post_app_service.get_posts_to_schedule(user_id=user.id)
            if random_post_ids and len(random_post_ids) > 0:
                #send mail
                random_post_ids = [str(id) for id in random_post_ids]
                post_app_service.send_posts_in_email(user=user, post_ids=random_post_ids)
        session.close()
        return "Notification task completed!"
    except Exception as e:
        return f"ERROR:{e}"