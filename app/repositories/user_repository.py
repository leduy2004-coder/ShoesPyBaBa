from sqlalchemy.orm import Session
from app.models.user_model import User
from typing import Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(
                User.email == email,
                User.status == 1
            )
            .first()
        )

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self) -> None:
        """
        Commits changes to the database.
        Note: The object should be modified before calling this.
        """
        self.db.commit()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()