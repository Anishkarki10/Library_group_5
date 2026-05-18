from flask import Flask
from app.routes.auth import AuthRoutes

def create_app():
    app = Flask(__name__)

    auth_routes = AuthRoutes() 
    app.register_blueprint(auth_routes.register()) 


    return app
