import uuid
from sqlmodel import select

from src.infrastructure.scheduler.celery import app
from src.domain.models import Otp
from src.setup.config.database import get_session

@app.task
def delete_otp(user_id:uuid.UUID):
    sessions = get_session()
    session = list(sessions)[0]
    otp = session.scalars(
            select(Otp).where(Otp.user_id == user_id)
        ).first()
    if not otp:
        return "Otp not found!"
    session.delete(otp)
    session.commit()
    session.close()
    return "Otp deleted!"