from flask import Blueprint
from app.controllers.auth import AuthController
class UserRoutes:
    def __init__(self):
        self.bp = Blueprint("users", __name__)
        self.controller = AuthController()

    def register(self):
        self.bp.route("/login")(
            self.controller.login
        )
        self.bp.route("/register")(
            self.controller.register
        )
        return self.bp