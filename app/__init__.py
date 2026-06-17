from flask import Flask
from app.routes.auth import AuthRoutes
from app.models.database import Database
from flask import Flask, render_template
import config
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    # Book cover image upload folder
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "books"
    )

    # Create folder automatically if it does not exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Create database tables
    with app.app_context():
        Database.create_tables()

    # Register routes
    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.register())

    # 404 error
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("notfound.html"), 404

    return app