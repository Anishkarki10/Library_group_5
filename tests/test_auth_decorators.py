from flask import Flask, Blueprint
from app.auth import login_required, admin_required


def make_app():
    app = Flask(__name__)
    app.secret_key = "secret"
    bp = Blueprint("auth", __name__)

    @bp.route("/login")
    def login(): return "login"

    @bp.route("/logout")
    def logout(): return "logout"

    @bp.route("/home")
    @login_required
    def home(): return "home"

    @bp.route("/admin-only")
    @admin_required
    def admin_only(): return "admin"

    app.register_blueprint(bp)
    return app


def test_login_required_redirects_guest():
    client = make_app().test_client()
    response = client.get("/home")
    assert response.status_code == 302
    assert "/login" in response.location


def test_login_required_allows_logged_in_user():
    client = make_app().test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "user"
    response = client.get("/home")
    assert response.status_code == 200
    assert response.data.decode() == "home"


def test_admin_required_redirects_guest():
    client = make_app().test_client()
    response = client.get("/admin-only")
    assert response.status_code == 302
    assert "/login" in response.location


def test_admin_required_blocks_normal_user():
    client = make_app().test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "user"
    response = client.get("/admin-only")
    assert response.status_code == 302
    assert "/logout" in response.location


def test_admin_required_allows_admin():
    client = make_app().test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "admin"
    response = client.get("/admin-only")
    assert response.status_code == 200
    assert response.data.decode() == "admin"
