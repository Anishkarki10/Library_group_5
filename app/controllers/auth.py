"""
=============================================================
  OOP Concept: INHERITANCE & POLYMORPHISM (Auth Controller)
=============================================================
"""

import os
import random
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, session, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.models.book import Book

from app.models.reservation import Reservation


class AuthController(BaseController):
    def __init__(self):
        self.user_model = User()
        self.book_model = Book()
        self.reservation_model = Reservation()

    # ── Book Image Validation ────────────────────────────────

    def allowed_file(self, filename):
        allowed_extensions = {"png", "jpg", "jpeg", "webp"}
        return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

    # ── Add Book ─────────────────────────────────────────────

    def add_book(self):
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            genre = request.form.get("genre", "").strip()
            total = request.form.get("total", "").strip()
            available_count = request.form.get("available_count", "").strip()
            location = request.form.get("location", "").strip()
            image_file = request.files.get("image")

            if not title or not author or not genre or not total or not available_count or not location:
                flash("All book fields are required.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            try:
                total = int(total)
                available_count = int(available_count)
            except ValueError:
                flash("Total and available count must be numbers.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            if total < 1:
                flash("Total books must be at least 1.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            if available_count < 0:
                flash("Available count cannot be negative.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            if available_count > total:
                flash("Available count cannot be greater than total books.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            image_name = None

            if image_file and image_file.filename:
                if not self.allowed_file(image_file.filename):
                    flash("Only png, jpg, jpeg, and webp images are allowed.", "danger")
                    return redirect(url_for("auth.dashboard") + "#books")

                image_name = secure_filename(image_file.filename)
                image_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    image_name
                )

                image_file.save(image_path)

            new_book = Book(
                title=title,
                author=author,
                genre=genre,
                total=total,
                available_count=available_count,
                location=location,
                image=image_name
            )

            new_book.save()

            flash("Book added successfully.", "success")
            return redirect(url_for("auth.dashboard") + "#books")

        return redirect(url_for("auth.dashboard"))

    # ── Delete Book ──────────────────────────────────────────

    def delete_book(self, id):
        book = self.book_model.find_by_id(id)

        if not book:
            flash("Book not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#books")

        if book.get("image"):
            image_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                book["image"]
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        self.book_model.delete(id)

        flash("Book deleted successfully.", "success")
        return redirect(url_for("auth.dashboard") + "#books")

    # ── Home / Student Dashboard ─────────────────────────────

    def home(self):
        user_id = self.get_current_user_id()

        books = self.book_model.get_all()
        reservations = self.reservation_model.get_user_reservations(user_id)

        active_reservations = []
        reading_history = []
        cancelled_reservations = []

        for item in reservations:
            if item["status"] == "returned":
                reading_history.append(item)
            elif item["status"] == "cancelled":
                cancelled_reservations.append(item)
            else:
                active_reservations.append(item)

        reservation_success = session.pop("reservation_success", None)

        return render_template(
            "home.html",
            books=books,
            reservations=active_reservations,
            reading_history=reading_history,
            cancelled_reservations=cancelled_reservations,
            reservation_success=reservation_success
        )



    # ── Student Login ────────────────────────────────────────

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

    # ── Register ─────────────────────────────────────────────

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

    # ── Logout ───────────────────────────────────────────────

    def logout(self):
        session.clear()
        return self.flash_and_redirect(
            "Logged out successfully.", "success", "auth.login"
        )

    # ── Admin Dashboard ──────────────────────────────────────
    def dashboard(self):
        users = self.user_model.find_all()
        books = self.book_model.get_all()
        reservations = self.reservation_model.get_all_reservations()

        return render_template(
            "dashboard.html",
            users=users,
            books=books,
            borrowings=reservations,
            reservations=reservations,
            overdue_count=0
        )

    # ── Change Password ──────────────────────────────────────

    def change_password(self):
        user_id = self.get_current_user_id()

        if not user_id:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        user_data = self.user_model.find_by_id(user_id)

        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.logout"))

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not current_password or not new_password or not confirm_password:
            flash("All password fields are required.", "danger")
            return redirect(url_for("auth.home") + "#password")

        if len(new_password) < 6:
            flash("New password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.home") + "#password")

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("auth.home") + "#password")

        if current_password == new_password:
            flash("New password must be different from current password.", "danger")
            return redirect(url_for("auth.home") + "#password")

        user_obj = User.from_db(user_data)

        if not user_obj.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("auth.home") + "#password")

        user_obj.set_password(new_password)
        user_obj.update_profile(user_id, update_password=True)

        session.clear()
        flash("Password changed successfully. Please login again.", "success")
        return redirect(url_for("auth.login"))

    # ── Forgot Password: Send OTP ────────────────────────────

    def forgot_password(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip()

            if not email:
                flash("Email is required.", "danger")
                return redirect(url_for("auth.forgot_password"))

            user = self.user_model.find_by_email(email)

            if not user:
                flash("No account found with this email.", "danger")
                return redirect(url_for("auth.forgot_password"))

            user_role = user["role"] if isinstance(user, dict) else user.role

            if user_role == "admin":
                flash("Admin password cannot be reset from student page.", "danger")
                return redirect(url_for("auth.forgot_password"))

            otp = str(random.randint(100000, 999999))
            hashed_otp = generate_password_hash(otp)
            expiry_time = datetime.now() + timedelta(minutes=5)

            self.user_model.save_reset_otp(email, hashed_otp, expiry_time)

            print("PASSWORD RESET OTP:", otp)

            session["reset_email"] = email

            flash("OTP has been generated. Check terminal for testing.", "success")
            return redirect(url_for("auth.verify_otp"))

        return render_template("forgot.html")

    # ── Verify OTP and Reset Password ────────────────────────

    def verify_otp(self):
        if "reset_email" not in session:
            flash("Please enter your email first.", "warning")
            return redirect(url_for("auth.forgot_password"))

        email = session["reset_email"]

        if request.method == "POST":
            otp = request.form.get("otp", "").strip()
            new_password = request.form.get("new_password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            if not otp or not new_password or not confirm_password:
                flash("All fields are required.", "danger")
                return redirect(url_for("auth.verify_otp"))

            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("auth.verify_otp"))

            if len(new_password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return redirect(url_for("auth.verify_otp"))

            user = self.user_model.find_by_email(email)

            if not user:
                flash("User not found.", "danger")
                return redirect(url_for("auth.forgot_password"))

            saved_otp = user["reset_otp"]
            expiry_time = user["reset_otp_expires"]

            if not saved_otp or not expiry_time:
                flash("OTP not found. Please request a new OTP.", "danger")
                return redirect(url_for("auth.forgot_password"))

            if isinstance(expiry_time, str):
                expiry_time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")

            if datetime.now() > expiry_time:
                flash("OTP expired. Please request a new OTP.", "danger")
                return redirect(url_for("auth.forgot_password"))

            if not check_password_hash(saved_otp, otp):
                flash("Invalid OTP.", "danger")
                return redirect(url_for("auth.verify_otp"))

            hashed_password = generate_password_hash(new_password)
            self.user_model.update_password_by_email(email, hashed_password)

            session.pop("reset_email", None)

            flash("Password reset successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        return render_template("verify_otp.html", email=email)

    # ── Add User ─────────────────────────────────────────────

    def add_user(self):
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()
            role = request.form.get("role", "user").strip()

            if not name or not email or not password or not confirm_password:
                flash("All fields are required.", "danger")
                return render_template("addUser.html")

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("addUser.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("addUser.html")

            if role not in ["user", "admin"]:
                flash("Invalid role selected.", "danger")
                return render_template("addUser.html")

            new_user = User(
                name=name,
                email=email,
                password=password,
                role=role
            )

            if new_user.email_exists():
                flash("Email already exists.", "danger")
                return render_template("addUser.html")

            new_user.save()

            flash("User added successfully.", "success")
            return redirect(url_for("auth.dashboard"))

        return render_template("addUser.html")

    # ── Edit User ────────────────────────────────────────────

    def editUsers(self, id):
        user_data = self.user_model.find_by_id(id)

        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("auth.dashboard"))

        user_obj = User.from_db(user_data)

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            password = request.form.get("password", "")
            role = request.form.get("role", "user")

            if not name or not email:
                flash("Name and email are required.", "danger")
                return render_template("editUser.html", user=user_data)

            user_obj.name = name
            user_obj.email = email
            user_obj.role = role

            update_password = False

            if password:
                if len(password) < 6:
                    flash("Password must be at least 6 characters.", "danger")
                    return render_template("editUser.html", user=user_data)

                user_obj.set_password(password)
                update_password = True

            user_obj.update(user_id=id, update_password=update_password)

            flash("User updated successfully.", "success")
            return redirect(url_for("auth.dashboard"))

        return render_template("editUser.html", user=user_data)

    # ── Delete User ──────────────────────────────────────────

    def deleteUser(self, id):
        if request.method == "POST":
            user = self.user_model.find_by_id(id)

            if not user:
                flash("User not found.", "danger")
                return redirect(url_for("auth.dashboard"))

            user_role = user["role"] if isinstance(user, dict) else user.role

            if user_role == "admin":
                flash("Admin cannot be deleted.", "danger")
                return redirect(url_for("auth.dashboard"))

            self.user_model.delete_by_id(id)
            flash("User deleted successfully.", "success")

        return redirect(url_for("auth.dashboard"))

# reserve book
    def reserve_book(self, book_id):
        user_id = self.get_current_user_id()

        if not user_id:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        book = self.book_model.find_by_id(book_id)

        if not book:
            flash("Book not found.", "danger")
            return redirect(url_for("auth.home"))

        if book["available_count"] <= 0:
            flash("This book is not available right now.", "danger")
            return redirect(url_for("auth.home"))

        if self.reservation_model.already_reserved(user_id, book_id):
            flash("You already reserved this book.", "warning")
            return redirect(url_for("auth.home"))

        due_date = datetime.now() + timedelta(days=14)

        self.reservation_model.create(
            user_id=user_id,
            book_id=book_id,
            due_date=due_date.date()
        )

        self.book_model.decrease_available(book_id)

        session["reservation_success"] = {
            "title": book["title"],
            "location": book["location"]
        }

        return redirect(url_for("auth.home") + "#dashboard")
    # ── Student Request Cancel Reservation ───────────────────

    def request_cancel_reservation(self, reservation_id):
        user_id = self.get_current_user_id()

        if not user_id:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.home") + "#dashboard")

        if reservation["user_id"] != user_id:
            flash("You cannot cancel this reservation.", "danger")
            return redirect(url_for("auth.home") + "#dashboard")

        if reservation["status"] != "reserved":
            flash("Only active reservations can request cancellation.", "warning")
            return redirect(url_for("auth.home") + "#dashboard")

        self.reservation_model.request_cancel(reservation_id, user_id)

        flash("Cancel request sent to admin for approval.", "success")
        return redirect(url_for("auth.home") + "#dashboard")

    # ── Admin Approve Cancel Reservation ─────────────────────

    def approve_cancel_reservation(self, reservation_id):
        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] != "cancel_requested":
            flash("This reservation does not have a cancel request.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        self.reservation_model.approve_cancel(reservation_id)
        self.book_model.increase_available(reservation["book_id"])

        flash("Cancel request approved. Book is available again.", "success")
        return redirect(url_for("auth.dashboard") + "#circulation")

    # ── Admin Reject Cancel Reservation ──────────────────────

    def reject_cancel_reservation(self, reservation_id):
        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] != "cancel_requested":
            flash("This reservation does not have a cancel request.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        self.reservation_model.reject_cancel(reservation_id)

        flash("Cancel request rejected. Reservation is still active.", "success")
        return redirect(url_for("auth.dashboard") + "#circulation")

    # ── Admin Return Book ────────────────────────────────────

    def return_book(self, reservation_id):
        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] == "returned":
            flash("Book is already returned.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] not in ["reserved", "borrowed", "renew_requested"]:
            flash("Only active borrowed/reserved books can be returned.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        self.reservation_model.mark_returned(reservation_id)
        self.book_model.increase_available(reservation["book_id"])

        flash("Book returned successfully.", "success")
        return redirect(url_for("auth.dashboard") + "#circulation")
        # ── Admin Mark Book Picked Up ────────────────────────────

    def mark_book_picked_up(self, reservation_id):
        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] != "reserved":
            flash("Only reserved books can be marked as picked up.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        due_date = datetime.now() + timedelta(days=15)

        self.reservation_model.mark_picked_up(
            reservation_id,
            due_date.date()
        )

        flash("Book marked as picked up. Student must return it within 15 days.", "success")
        return redirect(url_for("auth.dashboard") + "#circulation")

    # ── Student Request Renew ────────────────────────────────

    def request_renew_book(self, reservation_id):
        user_id = self.get_current_user_id()

        if not user_id:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.home") + "#dashboard")

        if reservation["user_id"] != user_id:
            flash("You cannot renew this book.", "danger")
            return redirect(url_for("auth.home") + "#dashboard")

        if reservation["status"] != "borrowed":
            flash("Only borrowed books can be renewed.", "warning")
            return redirect(url_for("auth.home") + "#dashboard")

        self.reservation_model.request_renew(reservation_id, user_id)

        flash("Renew request sent to admin for approval.", "success")
        return redirect(url_for("auth.home") + "#dashboard")

    # ── Admin Approve Renew ──────────────────────────────────

    def approve_renew_book(self, reservation_id):
        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] != "renew_requested":
            flash("This book does not have a renew request.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        new_due_date = datetime.now() + timedelta(days=15)

        self.reservation_model.approve_renew(
            reservation_id,
            new_due_date.date()
        )

        flash("Renew request approved. Due date extended by 15 days.", "success")
        return redirect(url_for("auth.dashboard") + "#circulation")

    # ── Admin Reject Renew ───────────────────────────────────

    def reject_renew_book(self, reservation_id):
        reservation = self.reservation_model.find_by_id(reservation_id)

        if not reservation:
            flash("Reservation not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#circulation")

        if reservation["status"] != "renew_requested":
            flash("This book does not have a renew request.", "warning")
            return redirect(url_for("auth.dashboard") + "#circulation")

        self.reservation_model.reject_renew(reservation_id)

        flash("Renew request rejected. Student must return the book by the current due date.", "success")
        return redirect(url_for("auth.dashboard") + "#circulation")
    
    # ── Edit Book ────────────────────────────────────────────

    def edit_book(self, id):
        book = self.book_model.find_by_id(id)

        if not book:
            flash("Book not found.", "danger")
            return redirect(url_for("auth.dashboard") + "#books")

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            genre = request.form.get("genre", "").strip()
            total = request.form.get("total", "").strip()
            available_count = request.form.get("available_count", "").strip()
            location = request.form.get("location", "").strip()
            image_file = request.files.get("image")

            if not title or not author or not genre or not total or not available_count or not location:
                flash("All book fields are required.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            try:
                total = int(total)
                available_count = int(available_count)
            except ValueError:
                flash("Total and available count must be numbers.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            if total < 1:
                flash("Total books must be at least 1.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            if available_count < 0:
                flash("Available count cannot be negative.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            if available_count > total:
                flash("Available count cannot be greater than total books.", "danger")
                return redirect(url_for("auth.dashboard") + "#books")

            image_name = None

            if image_file and image_file.filename:
                if not self.allowed_file(image_file.filename):
                    flash("Only png, jpg, jpeg, and webp images are allowed.", "danger")
                    return redirect(url_for("auth.dashboard") + "#books")

                image_name = secure_filename(image_file.filename)

                image_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    image_name
                )

                image_file.save(image_path)

                if book.get("image"):
                    old_image_path = os.path.join(
                        current_app.config["UPLOAD_FOLDER"],
                        book["image"]
                    )

                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

            self.book_model.update(
                book_id=id,
                title=title,
                author=author,
                genre=genre,
                total=total,
                available_count=available_count,
                location=location,
                image=image_name
            )

            flash("Book updated successfully.", "success")
            return redirect(url_for("auth.dashboard") + "#books")

        return redirect(url_for("auth.dashboard") + "#books")