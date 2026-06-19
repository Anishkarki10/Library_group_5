from flask import Blueprint

from app.controllers.auth import AuthController
from app.auth import login_required, admin_required


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
        # ── Student Login ────────────────────────────────────
        self.bp.route("/login", methods=["GET", "POST"])(
            self.controller.login
        )

        # ── Forgot Password OTP ──────────────────────────────
        self.bp.route("/forgot-password", methods=["GET", "POST"])(
            self.controller.forgot_password
        )

        self.bp.route("/verify-otp", methods=["GET", "POST"])(
            self.controller.verify_otp
        )

        # ── Admin Login ──────────────────────────────────────
        self.bp.route("/admin", methods=["GET", "POST"])(
            self.controller.admin
        )

        # ── Register User ────────────────────────────────────
        self.bp.route("/register", methods=["GET", "POST"])(
            self.controller.register
        )

        # ── Student Home / Dashboard ─────────────────────────
        self.bp.route("/", methods=["GET", "POST"])(
            login_required(self.controller.home)
        )

        # ── Logout ───────────────────────────────────────────
        self.bp.route("/logout", methods=["GET", "POST"])(
            self.controller.logout
        )

        # ── Admin Dashboard ──────────────────────────────────
        self.bp.route("/dashboard", methods=["GET", "POST"])(
            admin_required(self.controller.dashboard)
        )

        # ── Add User ─────────────────────────────────────────
        self.bp.route("/add-user", methods=["GET", "POST"])(
            admin_required(self.controller.add_user)
        )

        # ── Edit User ────────────────────────────────────────
        self.bp.route("/edit/<int:id>", methods=["GET", "POST"])(
            admin_required(self.controller.editUsers)
        )

        # ── Delete User ──────────────────────────────────────
        self.bp.route("/delete/<int:id>", methods=["POST"])(
            admin_required(self.controller.deleteUser)
        )

        # ── Student Change Password ──────────────────────────
        self.bp.route("/change-password", methods=["POST"])(
            login_required(self.controller.change_password)
        )

        # ── Add Book From Admin Dashboard ────────────────────
        self.bp.route("/add-book", methods=["POST"])(
            admin_required(self.controller.add_book)
        )

        # ── Edit Book From Admin Dashboard ───────────────────
        self.bp.route("/edit-book/<int:id>", methods=["POST"])(
            admin_required(self.controller.edit_book)
        )

        # ── Delete Book From Admin Dashboard ─────────────────
        self.bp.route("/delete-book/<int:id>", methods=["POST"])(
            admin_required(self.controller.delete_book)
        )

        # ── Student Reserve Book ─────────────────────────────
        self.bp.route("/reserve-book/<int:book_id>", methods=["POST"])(
            login_required(self.controller.reserve_book)
        )

        # ── Admin Return Book ────────────────────────────────
        self.bp.route("/return-book/<int:reservation_id>", methods=["POST"])(
            admin_required(self.controller.return_book)
        )

        # ── Student Request Cancel Reservation ───────────────
        self.bp.route("/request-cancel-reservation/<int:reservation_id>", methods=["POST"])(
            login_required(self.controller.request_cancel_reservation)
        )

        # ── Admin Approve Cancel Reservation ─────────────────
        self.bp.route("/approve-cancel-reservation/<int:reservation_id>", methods=["POST"])(
            admin_required(self.controller.approve_cancel_reservation)
        )

        # ── Admin Reject Cancel Reservation ──────────────────
        self.bp.route("/reject-cancel-reservation/<int:reservation_id>", methods=["POST"])(
            admin_required(self.controller.reject_cancel_reservation)
        )

        # ── Admin Mark Book Picked Up ────────────────────────
        self.bp.route("/mark-picked-up/<int:reservation_id>", methods=["POST"])(
            admin_required(self.controller.mark_book_picked_up)
        )

        # ── Student Request Renew Book ───────────────────────
        self.bp.route("/request-renew-book/<int:reservation_id>", methods=["POST"])(
            login_required(self.controller.request_renew_book)
        )

        # ── Admin Approve Renew Book ─────────────────────────
        self.bp.route("/approve-renew-book/<int:reservation_id>", methods=["POST"])(
            admin_required(self.controller.approve_renew_book)
        )

        # ── Admin Reject Renew Book ──────────────────────────
        self.bp.route("/reject-renew-book/<int:reservation_id>", methods=["POST"])(
            admin_required(self.controller.reject_renew_book)
        )

        # ── Add E-Book From Admin Dashboard ──────────────────
        self.bp.route("/add-ebook", methods=["POST"])(
            admin_required(self.controller.add_ebook)
        )

        # ── Edit E-Book From Admin Dashboard ─────────────────
        self.bp.route("/edit-ebook/<int:ebook_id>", methods=["POST"])(
            admin_required(self.controller.edit_ebook)
        )

        # ── Delete E-Book From Admin Dashboard ───────────────
        self.bp.route("/delete-ebook/<int:ebook_id>", methods=["POST"])(
            admin_required(self.controller.delete_ebook)
        )

        return self.bp