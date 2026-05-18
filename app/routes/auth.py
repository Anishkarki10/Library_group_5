from flask import Blueprint
from app.controllers.auth import AuthController
from app.controllers.auth import AuthController
class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
        self.bp.route("/login", methods=["GET", "POST","PUT"])(
            self.controller.login
        )
        self.bp.route("/register", methods=["GET", "POST"])(
            self.controller.register
        )
        self.bp.route("/", methods=["GET", "POST"])(
            self.controller.home
        )
        return self.bp