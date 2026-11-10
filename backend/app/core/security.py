from datetime import datetime, timedelta, timezone
import hashlib, hmac, secrets
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import JWT_SECRET, JWT_EXPIRE_MINUTES
from app.core.database import get_db
from app.models.models import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, salt, expected = encoded.split("$")
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 180000)
        return algo == "pbkdf2_sha256" and hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False

def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    data = {"sub": str(user.id), "role": user.role, "iat": now,
            "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES)}
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        uid = int(data["sub"])
    except (JWTError, ValueError, KeyError, TypeError):
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate":"Bearer"})
    user = db.get(User, uid)
    if not user or user.role != data.get("role"):
        raise HTTPException(401, "Invalid or expired token")
    return user

def require_role(*roles):
    def check(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Not authorized")
        return user
    return check
