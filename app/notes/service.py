from sqlalchemy import select, text
from ..extensions import db
from ..models import Note
from ..errors import ApiError


def create_note(user_id: int, title: str, content: str) -> Note:
    n = Note(user_id=user_id, title=title, content=content)
    db.session.add(n)
    db.session.commit()
    return n


def list_notes(user_id: int) -> list[Note]:
    return db.session.execute(
        select(Note).where(Note.user_id == user_id).order_by(Note.id.desc())
    ).scalars().all()


def get_note_owned(user_id: int, note_id: int) -> Note:
    n = db.session.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    ).scalar_one_or_none()

    if not n:
        raise ApiError("Not Found", 404)

    return n


def update_note(user_id: int, note_id: int, title: str, content: str) -> Note:
    n = get_note_owned(user_id, note_id)
    n.title = title
    n.content = content
    db.session.commit()
    return n


def delete_note(user_id: int, note_id: int):
    n = get_note_owned(user_id, note_id)
    db.session.delete(n)
    db.session.commit()


# Prepared statement example (for demo)
def safe_prepared_query_example(user_id: int, note_id: int) -> dict | None:
    sql = text("SELECT id, user_id, title, content FROM notes WHERE id = :nid AND user_id = :uid")
    row = db.session.execute(sql, {"nid": note_id, "uid": user_id}).mappings().first()
    return dict(row) if row else None
