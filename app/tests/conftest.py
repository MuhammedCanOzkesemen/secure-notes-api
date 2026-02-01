import pytest
from app import create_app
from app.extensions import db
from app.models import User, Note

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_COOKIE_SECURE"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def register(client, email, username, password):
    return client.post("/auth/register", json={
        "email": email,
        "username": username,
        "password": password
    })

def login(client, email, password):
    return client.post("/auth/login", json={
        "email": email,
        "password": password
    })
