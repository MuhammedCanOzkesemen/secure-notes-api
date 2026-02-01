import logging
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, jwt_required, get_jwt_identity, get_jwt
)

from ..extensions import limiter, db
from ..models import User
from ..errors import ApiError
from ..utils import validate_password_policy
from .validators import validate_email, validate_required
from .service import create_user, authenticate, revoke_jti, is_jti_revoked
from . import bp
from sqlalchemy import select

log = logging.getLogger("security")

@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    errors = {}

    e = validate_required(email, "email")
    if e or not validate_email(email):
        errors["email"] = ["Invalid email"]

    e = validate_required(username, "username")
    if e:
        errors["username"] = [e]

    pw_errors = validate_password_policy(password)
    if pw_errors:
        errors["password"] = pw_errors

    if errors:
        raise ApiError("Validation error", 400, errors)

    u = create_user(email=email.strip().lower(), username=username.strip(), password=password)
    return jsonify({"id": u.id, "email": u.email, "username": u.username}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not validate_email(email) or not password:
        raise ApiError("Invalid credentials", 401)

    try:
        u = authenticate(email=email, password=password)
    except ApiError:
        log.info("Failed login attempt for email=%s ip=%s", email, request.remote_addr)
        raise

    access = create_access_token(identity=str(u.id), additional_claims={"role": u.role})
    refresh = create_refresh_token(identity=str(u.id), additional_claims={"role": u.role})

    resp = jsonify({"message": "Login successful"})
    set_access_cookies(resp, access)
    set_refresh_cookies(resp, refresh)
    return resp, 200


@bp.post("/logout")
@jwt_required(optional=True)
def logout():
    jwt_data = get_jwt() or {}
    jti = jwt_data.get("jti")
    ttype = jwt_data.get("type")
    if jti and ttype:
        revoke_jti(jti, ttype)

    resp = jsonify({"message": "Logged out"})
    unset_jwt_cookies(resp)
    return resp, 200


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    jwt_data = get_jwt()
    jti = jwt_data.get("jti")

    if is_jti_revoked(jti):
        raise ApiError("Token revoked", 401)

    revoke_jti(jti, "refresh")

    uid = get_jwt_identity()
    u = db.session.execute(select(User).where(User.id == int(uid))).scalar_one_or_none()
    if not u:
        raise ApiError("Invalid user", 401)

    access = create_access_token(identity=str(u.id), additional_claims={"role": u.role})
    new_refresh = create_refresh_token(identity=str(u.id), additional_claims={"role": u.role})

    resp = jsonify({"message": "Refreshed"})
    set_access_cookies(resp, access)
    set_refresh_cookies(resp, new_refresh)
    return resp, 200


@bp.get("/me")
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    u = db.session.execute(select(User).where(User.id == uid)).scalar_one()
    return jsonify({"id": u.id, "email": u.email, "username": u.username, "role": u.role}), 200
