import re
from werkzeug.security import generate_password_hash, check_password_hash

COMMON_PASSWORDS = {
    "password", "12345678", "qwerty", "letmein", "admin", "iloveyou", "welcome"
}

def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)

def validate_password_policy(pw: str) -> list[str]:
    errors = []
    if pw is None:
        return ["Password is required"]

    if len(pw) < 10:
        errors.append("Password must be at least 10 characters")

    if pw.lower() in COMMON_PASSWORDS:
        errors.append("Password is too common")

    if not re.search(r"[A-Z]", pw):
        errors.append("Password must contain an uppercase letter")

    if not re.search(r"[a-z]", pw):
        errors.append("Password must contain a lowercase letter")

    if not re.search(r"[0-9]", pw):
        errors.append("Password must contain a digit")

    if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]", pw):
        errors.append("Password must contain a special character")

    return errors
