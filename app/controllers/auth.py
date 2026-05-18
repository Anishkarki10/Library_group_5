from flask import render_template, request
class AuthController:
    def login(self):
        if request.method == "POST":
            print(request.form)

        return render_template("login.html")
    
    def register(self):
        return render_template("register.html")
    
    def home(self):
        a=["abishek bimali","test"]
        return render_template("home.html",name=a)
    