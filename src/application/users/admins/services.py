import uuid

from sqlmodel import Session

from src.interface.users.admins.schemas import CreateAdmin
from src.domain.users.admins.services import AdminService
from src.domain.models import Admin

class AdminAppService:
    """admin application service class"""
    def __init__(self, session:Session):
        self.db_session = session
        self.admin_service = AdminService(session=session)

    def get_admin_by_base_user_id(self, base_user_id:uuid.UUID) -> Admin:
        """get admin by base user id"""
        return self.admin_service.get_admin_by_base_user_id(base_user_id=base_user_id)

    def create_admin(self, admin:CreateAdmin) -> Admin:
        """create admin"""
        return self.admin_service.create(admin=admin)
    
    def delete_admin(self, base_user_id:uuid.UUID) -> None:
        admin = self.get_admin_by_base_user_id(base_user_id=base_user_id)
        if not admin:
            return None
        self.admin_service.delete(admin=admin)
        return None
    
    def create_admin_directly(self, base_user_id:uuid.UUID) -> Admin:
        """create admin when base_user is created"""
        admin = CreateAdmin(base_user_id=base_user_id)
        db_admin = self.create_admin(admin=admin)
        return db_admin