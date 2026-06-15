from flask import Blueprint
from app.controllers.auth import AuthController
from app.auth import login_required, admin_required


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
        # Student login
        self.bp.route("/login", methods=["GET", "POST"])(
            self.controller.login
        )

        # Forgot password OTP
        self.bp.route("/forgot-password", methods=["GET", "POST"])(
            self.controller.forgot_password
        )

        self.bp.route("/verify-otp", methods=["GET", "POST"])(
            self.controller.verify_otp
        )

        # Admin login
        self.bp.route("/admin", methods=["GET", "POST"])(
            self.controller.admin
        )

        # Register user
        self.bp.route("/register", methods=["GET", "POST"])(
            self.controller.register
        )

        # Student home/dashboard
        self.bp.route("/", methods=["GET", "POST"])(
            login_required(self.controller.home)
        )

        # Logout
        self.bp.route("/logout", methods=["GET", "POST"])(
            self.controller.logout
        )

        # Admin dashboard
        self.bp.route("/dashboard", methods=["GET", "POST"])(
            admin_required(self.controller.dashboard)
        )

        # Add user
        self.bp.route("/add-user", methods=["GET", "POST"])(
            admin_required(self.controller.add_user)
        )

        # Edit user
        self.bp.route("/edit/<int:id>", methods=["GET", "POST"])(
            admin_required(self.controller.editUsers)
        )

        # Delete user
        self.bp.route("/delete/<int:id>", methods=["POST"])(
            admin_required(self.controller.deleteUser)
        )

        # Student change password
        self.bp.route("/change-password", methods=["POST"])(
            login_required(self.controller.change_password)
        )

        # Add book from admin dashboard
        self.bp.route("/add-book", methods=["POST"])(
            admin_required(self.controller.add_book)
        )

        # Delete book from admin dashboard
        self.bp.route("/delete-book/<int:id>", methods=["POST"])(
            admin_required(self.controller.delete_book)
        )

        return self.bp