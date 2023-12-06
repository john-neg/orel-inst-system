from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash

from app.db.auth_models import Users
from app.services.base_db_service import BaseDBService, ModelType


@dataclass
class UsersCRUDService(BaseDBService[Users]):
    @staticmethod
    def get_password_hash(password) -> str:
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash, password) -> bool:
        return check_password_hash(password_hash, password)

    def create_user(self, username, password, role_id) -> ModelType:
        new_user = self.create(
            username=username,
            password_hash=self.get_password_hash(password),
            role_id=role_id,
        )
        return new_user

    def update_user(
        self,
        user_id: int,
        username: str | None = None,
        password: str | None = None,
        role_id: int | None = None,
    ) -> ModelType:
        update_dict = {}
        if username:
            update_dict["username"] = username
        if password:
            update_dict["password_hash"] = self.get_password_hash(password)
        if role_id:
            update_dict["role_id"] = role_id
        return self.update(user_id, **update_dict)
