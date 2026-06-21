def test_auth_routes_registers_expected_endpoints():
    from flask import Flask
    from app.routes.auth import AuthRoutes

    app = Flask(__name__)
    app.secret_key = "route-test"
    app.register_blueprint(AuthRoutes().register())

    endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}
    expected = {
        "auth.login", "auth.forgot_password", "auth.verify_otp", "auth.admin", "auth.register",
        "auth.home", "auth.logout", "auth.dashboard", "auth.add_user", "auth.editUsers",
        "auth.deleteUser", "auth.change_password", "auth.add_book", "auth.edit_book",
        "auth.delete_book", "auth.reserve_book", "auth.request_cancel_reservation",
        "auth.approve_cancel_reservation", "auth.reject_cancel_reservation", "auth.admin_cancel_reservation",
        "auth.return_book", "auth.mark_book_picked_up", "auth.request_renew_book",
        "auth.approve_renew_book", "auth.reject_renew_book", "auth.add_ebook", "auth.edit_ebook",
        "auth.delete_ebook"
    }
    assert expected.issubset(endpoints)
