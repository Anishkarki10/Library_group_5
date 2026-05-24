from flask import render_template
class Product:
    def getProduct(self):
        # logic
        p=["pro1","pro2"]
        return render_template("product/getproduct.html",a=p)