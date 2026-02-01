import re

def validate_email(email: str) -> bool:
    if not email:
        return False
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

def validate_required(value, name: str) -> str | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return f"{name} is required"
    return None
