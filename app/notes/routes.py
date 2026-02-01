import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from ..errors import ApiError
from .service import (
    create_note,
    list_notes,
    get_note_owned,
    update_note,
    delete_note,
    safe_prepared_query_example
)
from . import bp

log = logging.getLogger("security")


def require_role(role: str):
    def decorator(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != role:
                log.info("Forbidden role access role=%s required=%s ip=%s",
                         claims.get("role"), role, request.remote_addr)
                raise ApiError("Forbidden", 403)
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator


@bp.get("")
@jwt_required()
def notes_list():
    uid = int(get_jwt_identity())
    notes = list_notes(uid)
    return jsonify([
        {"id": n.id, "title": n.title, "content": n.content}
        for n in notes
    ]), 200


@bp.post("")
@jwt_required()
def notes_create():
    uid = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    errors = {}
    if not title:
        errors["title"] = ["title is required"]
    if not content:
        errors["content"] = ["content is required"]

    if errors:
        raise ApiError("Validation error", 400, errors)

    n = create_note(uid, title, content)
    return jsonify({"id": n.id, "title": n.title, "content": n.content}), 201


@bp.get("/<int:note_id>")
@jwt_required()
def notes_get(note_id: int):
    uid = int(get_jwt_identity())
    n = get_note_owned(uid, note_id)
    return jsonify({"id": n.id, "title": n.title, "content": n.content}), 200


@bp.put("/<int:note_id>")
@jwt_required()
def notes_update(note_id: int):
    uid = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        raise ApiError("Validation error", 400, {"note": ["title and content required"]})

    n = update_note(uid, note_id, title, content)
    return jsonify({"id": n.id, "title": n.title, "content": n.content}), 200


@bp.delete("/<int:note_id>")
@jwt_required()
def notes_delete(note_id: int):
    uid = int(get_jwt_identity())
    delete_note(uid, note_id)
    return jsonify({"message": "Deleted"}), 200


# Admin-only prepared statement demo
@bp.get("/admin/prepared/<int:note_id>")
@require_role("ROLE_ADMIN")
def admin_prepared(note_id: int):
    uid = int(get_jwt_identity())
    row = safe_prepared_query_example(uid, note_id)
    if not row:
        raise ApiError("Not Found", 404)
    return jsonify(row), 200
