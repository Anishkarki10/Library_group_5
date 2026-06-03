"""
=============================================================
  OOP Concept: INHERITANCE & POLYMORPHISM (Auth Controller)
=============================================================
  - AuthController INHERITS from BaseController.
  - It gets all helper methods (get_form_data, is_logged_in)
    from the parent FOR FREE — no need to rewrite them!
  - Each method in this class handles one authentication task.
=============================================================
"""

from flask import render_template, redirect, url_for, session, flash, request
from app.controllers.base_controller import BaseController
from app.models.user import User


class AuthController(BaseController):
    """
    Handles authentication: login, register, logout, dashboard, profile.

    Inherits from BaseController:
      - get_form_data()
      - is_logged_in()
      - get_current_user_id()
      - flash_and_redirect()
    """

    def __init__(self):
        self.user_model = User()

    # ── Home / Student Dashboard ─────────────────────────────

    def home(self):
        return render_template("home.html")

    # ── Student / Normal Login ───────────────────────────────

    def login(self):
        if self.is_logged_in():
            if session.get("role") != "admin":
                return redirect(url_for("auth.home"))
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email, password = self.get_form_data("email", "password")
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template("login.html")

            user_data = self.user_model.find_by("email", email)

            if user_data:
                user = User.from_db(user_data)

                if user.check_password(password):
                    session["user_id"] = user_data["id"]
                    session["user_name"] = user_data["name"]
                    session["role"] = user_data["role"]

                    if user_data["role"] != "admin":
                        return self.flash_and_redirect(
                            "Login successful!", "success", "auth.home"
                        )

                    return self.flash_and_redirect(
                        "Login successful!", "success", "auth.dashboard"
                    )

            flash("Invalid email or password.", "danger")

        return render_template("login.html")

    # ── Admin Login ──────────────────────────────────────────

    def admin(self):
        if self.is_logged_in():
            if session.get("role") == "admin":
                return redirect(url_for("auth.dashboard"))

            flash("Admin access required.", "danger")
            return redirect(url_for("auth.logout"))

        if request.method == "POST":
            email, password = self.get_form_data("email", "password")
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template("admin.html")

            user_data = self.user_model.find_by("email", email)

            if user_data:
                user = User.from_db(user_data)

                if user.check_password(password):
                    if user_data["role"] != "admin":
                        flash("You are not an admin.", "danger")
                        return render_template("admin.html")

                    session["user_id"] = user_data["id"]
                    session["user_name"] = user_data["name"]
                    session["role"] = user_data["role"]

                    return self.flash_and_redirect(
                        "Admin login successful!", "success", "auth.dashboard"
                    )

            flash("Invalid admin email or password.", "danger")

        return render_template("admin.html")

    # ── Register ────────────────────────────────────────────

    def register(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            student_id = request.form.get("student_id", "")
            phone = request.form.get("phone", "")
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            agree_terms = request.form.get("agree_terms")

            if not name or not student_id or not email or not phone or not password or not confirm_password:
                flash("All fields are required.", "danger")
                return render_template("register.html")

            if len(name) > 100:
                flash("Name must be under 100 characters.", "danger")
                return render_template("register.html")

            if len(phone) < 10:
                flash("Please enter a valid phone number.", "danger")
                return render_template("register.html")

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("register.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("register.html")

            if agree_terms != "yes":
                flash("You must agree to the terms and conditions.", "danger")
                return render_template("register.html")

            new_user = User(
                name=name,
                email=email,
                password=password,
                role="user"
            )

            if new_user.email_exists():
                flash("Email already exists.", "danger")
                return redirect(url_for("auth.register"))

            new_user.save()

            return self.flash_and_redirect(
                "Registration successful! Please login.",
                "success",
                "auth.login"
            )

        return render_template("register.html")
    # ── Logout ──────────────────────────────────────────────

    def logout(self):
        session.clear()
        return self.flash_and_redirect(
            "Logged out successfully.", "success", "auth.login"
        )

    # ── Admin Dashboard ─────────────────────────────────────

    def dashboard(self):
        users = self.user_model.find_all()
        print(users)
        return render_template("dashboard.html", users=users)

    # ── Profile ─────────────────────────────────────────────

    def profile(self):
        user_id = self.get_current_user_id()

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")

            if not name or not email:
                flash("Name and email are required.", "danger")
                user_data = self.user_model.find_by_id(user_id)
                return render_template("profile.html", user=user_data)

            user_obj = User(name=name, email=email)

            if user_obj.email_exists(exclude_id=user_id):
                flash("Email already taken by another user.", "danger")
                user_data = self.user_model.find_by_id(user_id)
                return render_template("profile.html", user=user_data)

            update_password = False

            if new_password:
                if len(new_password) < 6:
                    flash("New password must be at least 6 characters.", "danger")
                    user_data = self.user_model.find_by_id(user_id)
                    return render_template("profile.html", user=user_data)

                stored_data = self.user_model.find_by_id(user_id)
                stored_user = User.from_db(stored_data)

                if not stored_user.check_password(current_password):
                    flash("Current password is incorrect.", "danger")
                    user_data = self.user_model.find_by_id(user_id)
                    return render_template("profile.html", user=user_data)

                user_obj.set_password(new_password)
                update_password = True

            user_obj.update_profile(user_id, update_password=update_password)
            session["user_name"] = name

            return self.flash_and_redirect(
                "Profile updated successfully!", "success", "auth.profile"
            )

        user_data = self.user_model.find_by_id(user_id)
        return render_template("profile.html", user=user_data)

    # ── Edit User ───────────────────────────────────────────

    def editUsers(self, id):
        user_data = self.user_model.find_by_id(id)
        user_obj = User.from_db(user_data)

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            password = request.form.get("password", "")

            user_obj.name = name
            user_obj.email = email

            update_password = False

            if password:
                user_obj.set_password(password)
                update_password = True

            user_obj.update(user_id=id, update_password=update_password)

            return redirect(url_for("auth.dashboard"))

        return render_template("editUser.html", user=user_data)

    # ── Delete User ─────────────────────────────────────────

    def deleteUser(self, id):
        if request.method == "POST":
            self.user_model.delete_by_id(id)

        return redirect(url_for("auth.dashboard"))