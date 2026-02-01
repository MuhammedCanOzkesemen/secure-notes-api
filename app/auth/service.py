from sqlalchemy import select
from ..extensions import db
from ..models import User, RevokedToken
from ..utils import hash_password, verify_password
from ..errors import ApiError

def create_user(email: str, username: str, password: str, role: str = "ROLE_USER") -> User:
    existing = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        raise ApiError("Validation error", 400, {"email": ["Email already registered"]})

    u = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        role=role
    )
    db.session.add(u)
    db.session.commit()
    return u

def authenticate(email: str, password: str) -> User:
    u = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not u:
        raise ApiError("Invalid credentials", 401)

    if not verify_password(password, u.password_hash):
        raise ApiError("Invalid credentials", 401)

    return u

def revoke_jti(jti: str, token_type: str):
    if not jti:
        return
    exists = db.session.execute(select(RevokedToken).where(RevokedToken.jti == jti)).scalar_one_or_none()
    if not exists:
        db.session.add(RevokedToken(jti=jti, token_type=token_type))
        db.session.commit()

def is_jti_revoked(jti: str) -> bool:
    if not jti:
        return True
    found = db.session.execute(select(RevokedToken).where(RevokedToken.jti == jti)).scalar_one_or_none()
    return found is not None
