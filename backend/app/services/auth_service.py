from app.core.security import verify_password, create_access_token
from app.repositories.repository import UserRepository

class AuthService:
    @staticmethod
    def login(db, email, password):
        user = UserRepository.by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return {"access_token": create_access_token(user), "token_type": "bearer", "role": user.role, "name": user.name}
