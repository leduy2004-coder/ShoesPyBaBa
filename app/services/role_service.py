from sqlalchemy.orm import Session
from app.repositories.role_repository import RoleRepository
from typing import Optional

class RoleService:
    def __init__(self, db: Session):
        self.role_repo = RoleRepository(db)

    def get_role_name_by_id(self, role_id: int) -> Optional[str]:
        role = self.role_repo.get_by_id(role_id)
        if role:
            return role.name
        return None
