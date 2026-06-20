from flask import Blueprint
from app.controllers.productctrl import Product
class ProductRoutes:
    def __init__(self):
        self.bp = Blueprint("product", __name__)
        self.controller = Product()

    def register(self):
        self.bp.route("/get", methods=["GET", "POST"])(
            self.controller.getProduct
        )

        return self.bp