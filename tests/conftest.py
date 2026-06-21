import os
import pytest
from flask import Flask, Blueprint
from unittest.mock import MagicMock


def create_test_app(tmp_path=None):
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.config["TESTING"] = True

    if tmp_path:
        app.config["UPLOAD_FOLDER"] = str(tmp_path / "books")
        app.config["EBOOK_UPLOAD_FOLDER"] = str(tmp_path / "ebooks")
        app.config["EBOOK_COVER_UPLOAD_FOLDER"] = str(tmp_path / "ebooks" / "covers")
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(app.config["EBOOK_UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(app.config["EBOOK_COVER_UPLOAD_FOLDER"], exist_ok=True)

    bp = Blueprint("auth", __name__)
    endpoints = [
        ("/", "home"), ("/login", "login"), ("/admin", "admin"),
        ("/dashboard", "dashboard"), ("/register", "register"),
        ("/logout", "logout"), ("/forgot-password", "forgot_password"),
        ("/verify-otp", "verify_otp"), ("/add-user", "add_user"),
        ("/change-password", "change_password"),
    ]
    for url, endpoint in endpoints:
        bp.add_url_rule(url, endpoint=endpoint, view_func=lambda endpoint=endpoint: endpoint)
    app.register_blueprint(bp)
    return app


@pytest.fixture
def app(tmp_path):
    return create_test_app(tmp_path)


@pytest.fixture
def controller():
    from app.controllers.auth import AuthController
    c = AuthController()
    c.user_model = MagicMock()
    c.book_model = MagicMock()
    c.ebook_model = MagicMock()
    c.reservation_model = MagicMock()
    return c


@pytest.fixture
def user_row():
    return {"id": 1, "name": "Test User", "email": "test@example.com", "password": "hashed", "role": "user"}


@pytest.fixture
def admin_row():
    return {"id": 2, "name": "Admin", "email": "admin@example.com", "password": "hashed", "role": "admin"}


@pytest.fixture
def book_row():
    return {"id": 10, "title": "Atomic Habits", "author": "James Clear", "genre": "Personal Development", "total": 5, "available_count": 3, "location": "Shelf P-01", "image": None}


@pytest.fixture
def reservation_row():
    return {"id": 50, "user_id": 1, "book_id": 10, "status": "borrowed", "due_date": "2026-06-30"}
