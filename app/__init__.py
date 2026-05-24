from flask import Flask
from app.routes.auth import AuthRoutes
from app.models.database import Database
import config
def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    with app.app_context():
        Database.create_tables()  # Static method — called on the class, not an object


    auth_routes = AuthRoutes() 
    app.register_blueprint(auth_routes.register()) 
    return app
