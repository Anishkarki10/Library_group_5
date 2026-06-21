from datetime import datetime, timedelta, date
from unittest.mock import MagicMock, patch

from flask import get_flashed_messages, session
from werkzeug.security import generate_password_hash


@patch("app.controllers.auth.render_template")
def test_register_get(mock_render, app, controller):
    mock_render.return_value = "register_page"

    with app.test_request_context("/register", method="GET"):
        result = controller.register()

    assert result == "register_page"
    mock_render.assert_called_once_with("register.html")


@patch("app.controllers.auth.render_template")
def test_register_missing_fields(mock_render, app, controller):
    mock_render.return_value = "register_page"

    with app.test_request_context("/register", method="POST", data={}):
        result = controller.register()
        flashes = get_flashed_messages(with_categories=True)

    assert result == "register_page"
    assert ("danger", "All fields are required.") in flashes


@patch("app.controllers.auth.render_template")
def test_register_password_mismatch(mock_render, app, controller):
    mock_render.return_value = "register_page"

    data = {
        "name": "Alice",
        "student_id": "S001",
        "email": "alice@example.com",
        "phone": "9812345678",
        "password": "secret1",
        "confirm_password": "secret2",
        "agree_terms": "yes",
    }

    with app.test_request_context("/register", method="POST", data=data):
        result = controller.register()
        flashes = get_flashed_messages(with_categories=True)

    assert result == "register_page"
    assert ("danger", "Passwords do not match.") in flashes


@patch("app.controllers.auth.User")
def test_register_duplicate_email(mock_user_class, app, controller):
    fake_user = MagicMock()
    fake_user.email_exists.return_value = True
    mock_user_class.return_value = fake_user

    data = {
        "name": "Alice",
        "student_id": "S001",
        "email": "alice@example.com",
        "phone": "9812345678",
        "password": "secret1",
        "confirm_password": "secret1",
        "agree_terms": "yes",
    }

    with app.test_request_context("/register", method="POST", data=data):
        response = controller.register()
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    assert "/register" in response.location
    assert ("danger", "Email already exists.") in flashes
    fake_user.save.assert_not_called()


@patch("app.controllers.auth.User")
def test_register_success(mock_user_class, app, controller):
    fake_user = MagicMock()
    fake_user.email_exists.return_value = False
    mock_user_class.return_value = fake_user

    data = {
        "name": "Alice",
        "student_id": "S001",
        "email": "alice@example.com",
        "phone": "9812345678",
        "password": "secret1",
        "confirm_password": "secret1",
        "agree_terms": "yes",
    }

    with app.test_request_context("/register", method="POST", data=data):
        response = controller.register()
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    assert "/login" in response.location
    fake_user.save.assert_called_once()
    assert ("success", "Registration successful! Please login.") in flashes


@patch("app.controllers.auth.render_template")
def test_login_get(mock_render, app, controller):
    mock_render.return_value = "login_page"

    with app.test_request_context("/login", method="GET"):
        result = controller.login()

    assert result == "login_page"
    mock_render.assert_called_once_with("login.html")


@patch("app.controllers.auth.render_template")
def test_login_missing_fields(mock_render, app, controller):
    mock_render.return_value = "login_page"

    with app.test_request_context("/login", method="POST", data={"email": "", "password": ""}):
        result = controller.login()
        flashes = get_flashed_messages(with_categories=True)

    assert result == "login_page"
    assert ("danger", "Email and password are required.") in flashes


@patch("app.controllers.auth.User.from_db")
def test_login_success_user(mock_from_db, app, controller, user_row):
    controller.user_model.find_by.return_value = user_row
    fake_user = MagicMock()
    fake_user.check_password.return_value = True
    mock_from_db.return_value = fake_user

    with app.test_request_context("/login", method="POST", data={"email": "test@example.com", "password": "secret1"}):
        response = controller.login()
        flashes = get_flashed_messages(with_categories=True)

        # IMPORTANT: session must be checked while still inside request context
        assert session["user_id"] == 1
        assert session["user_name"] == "Test User"
        assert session["role"] == "user"

    assert response.status_code == 302
    assert response.location.endswith("/")
    assert ("success", "Login successful!") in flashes


@patch("app.controllers.auth.User.from_db")
def test_login_success_admin(mock_from_db, app, controller, admin_row):
    controller.user_model.find_by.return_value = admin_row
    fake_user = MagicMock()
    fake_user.check_password.return_value = True
    mock_from_db.return_value = fake_user

    with app.test_request_context("/login", method="POST", data={"email": "admin@example.com", "password": "admin123"}):
        response = controller.login()

        # IMPORTANT: session must be checked while still inside request context
        assert session["role"] == "admin"

    assert response.status_code == 302
    assert "/dashboard" in response.location


@patch("app.controllers.auth.User.from_db")
@patch("app.controllers.auth.render_template")
def test_login_wrong_password(mock_render, mock_from_db, app, controller, user_row):
    mock_render.return_value = "login_page"
    controller.user_model.find_by.return_value = user_row
    fake_user = MagicMock()
    fake_user.check_password.return_value = False
    mock_from_db.return_value = fake_user

    with app.test_request_context("/login", method="POST", data={"email": "test@example.com", "password": "bad"}):
        result = controller.login()
        flashes = get_flashed_messages(with_categories=True)

        # IMPORTANT: session must be checked while still inside request context
        assert "user_id" not in session

    assert result == "login_page"
    assert ("danger", "Invalid email or password.") in flashes


def test_logout(app, controller):
    with app.test_request_context("/logout"):
        session["user_id"] = 1
        session["user_name"] = "A"
        session["role"] = "user"

        response = controller.logout()
        flashes = get_flashed_messages(with_categories=True)

        # IMPORTANT: session must be checked while still inside request context
        assert "user_id" not in session
        assert "user_name" not in session
        assert "role" not in session

    assert response.status_code == 302
    assert "/login" in response.location
    assert ("success", "Logged out successfully.") in flashes


@patch("app.controllers.auth.render_template")
def test_forgot_password_get(mock_render, app, controller):
    mock_render.return_value = "forgot_page"

    with app.test_request_context("/forgot-password", method="GET"):
        result = controller.forgot_password()

    assert result == "forgot_page"
    mock_render.assert_called_once_with("forgot.html")


def test_forgot_password_unknown_email(app, controller):
    controller.user_model.find_by_email.return_value = None

    with app.test_request_context("/forgot-password", method="POST", data={"email": "none@example.com"}):
        response = controller.forgot_password()
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    assert "/forgot-password" in response.location
    assert ("danger", "No account found with this email.") in flashes


@patch("app.controllers.auth.random.randint", return_value=123456)
def test_forgot_password_success(mock_rand, app, controller, user_row):
    controller.user_model.find_by_email.return_value = user_row

    with app.test_request_context("/forgot-password", method="POST", data={"email": "test@example.com"}):
        response = controller.forgot_password()
        flashes = get_flashed_messages(with_categories=True)

        # IMPORTANT: session must be checked while still inside request context
        assert session["reset_email"] == "test@example.com"

    assert response.status_code == 302
    assert "/verify-otp" in response.location
    assert ("success", "OTP has been generated. Check terminal for testing.") in flashes
    controller.user_model.save_reset_otp.assert_called_once()


def test_verify_otp_requires_email(app, controller):
    with app.test_request_context("/verify-otp", method="GET"):
        response = controller.verify_otp()
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    assert "/forgot-password" in response.location
    assert ("warning", "Please enter your email first.") in flashes


def test_verify_otp_success(app, controller):
    controller.user_model.find_by_email.return_value = {
        "reset_otp": generate_password_hash("123456"),
        "reset_otp_expires": datetime.now() + timedelta(minutes=5),
    }

    data = {
        "otp": "123456",
        "new_password": "newpass1",
        "confirm_password": "newpass1",
    }

    with app.test_request_context("/verify-otp", method="POST", data=data):
        session["reset_email"] = "test@example.com"

        response = controller.verify_otp()
        flashes = get_flashed_messages(with_categories=True)

        # IMPORTANT: session must be checked while still inside request context
        assert "reset_email" not in session

    assert response.status_code == 302
    assert "/login" in response.location
    assert ("success", "Password reset successful. Please login.") in flashes
    controller.user_model.update_password_by_email.assert_called_once()
