from datetime import date
from flask import get_flashed_messages, session


def test_reserve_book_success(app, controller, book_row):
    controller.book_model.find_by_id.return_value = book_row
    controller.reservation_model.already_reserved.return_value = False

    with app.test_request_context("/reserve-book/10", method="POST"):
        session["user_id"] = 1

        response = controller.reserve_book(10)

        # IMPORTANT: session must be checked while still inside request context
        assert session["reservation_success"]["title"] == "Atomic Habits"
        assert session["reservation_success"]["location"] == book_row["location"]

    assert response.status_code == 302
    controller.reservation_model.create.assert_called_once()
    controller.book_model.decrease_available.assert_called_once_with(10)


def test_reserve_book_unavailable(app, controller, book_row):
    book_row["available_count"] = 0
    controller.book_model.find_by_id.return_value = book_row

    with app.test_request_context("/reserve-book/10", method="POST"):
        session["user_id"] = 1
        response = controller.reserve_book(10)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.create.assert_not_called()
    assert ("danger", "This book is not available right now.") in flashes


def test_reserve_book_duplicate(app, controller, book_row):
    controller.book_model.find_by_id.return_value = book_row
    controller.reservation_model.already_reserved.return_value = True

    with app.test_request_context("/reserve-book/10", method="POST"):
        session["user_id"] = 1
        response = controller.reserve_book(10)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.create.assert_not_called()
    assert ("warning", "You already reserved this book.") in flashes


def test_request_cancel_success(app, controller, reservation_row):
    reservation_row["status"] = "borrowed"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/request-cancel-reservation/50", method="POST"):
        session["user_id"] = 1
        response = controller.request_cancel_reservation(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.request_cancel.assert_called_once_with(50, 1)
    assert ("success", "Cancel request sent to admin for approval.") in flashes


def test_request_cancel_wrong_user(app, controller, reservation_row):
    reservation_row["user_id"] = 99
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/request-cancel-reservation/50", method="POST"):
        session["user_id"] = 1
        response = controller.request_cancel_reservation(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.request_cancel.assert_not_called()
    assert ("danger", "You cannot cancel this reservation.") in flashes


def test_approve_cancel_success(app, controller, reservation_row):
    reservation_row["status"] = "cancel_requested"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/approve-cancel-reservation/50", method="POST"):
        response = controller.approve_cancel_reservation(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.approve_cancel.assert_called_once_with(50)
    controller.book_model.increase_available.assert_called_once_with(10)
    assert ("success", "Cancel request approved. Book is available again.") in flashes


def test_reject_cancel_success(app, controller, reservation_row):
    reservation_row["status"] = "cancel_requested"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/reject-cancel-reservation/50", method="POST"):
        response = controller.reject_cancel_reservation(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.reject_cancel.assert_called_once_with(50)
    assert ("success", "Cancel request rejected. Reservation is still active.") in flashes


def test_admin_cancel_success(app, controller, reservation_row):
    reservation_row["status"] = "borrowed"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/admin-cancel-reservation/50", method="POST"):
        response = controller.admin_cancel_reservation(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.cancel_reservation.assert_called_once_with(50)
    controller.book_model.increase_available.assert_called_once_with(10)
    assert ("success", "Reservation cancelled successfully by admin.") in flashes


def test_return_book_success(app, controller, reservation_row):
    reservation_row["status"] = "borrowed"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/return-book/50", method="POST"):
        response = controller.return_book(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.mark_returned.assert_called_once_with(50)
    controller.book_model.increase_available.assert_called_once_with(10)
    assert ("success", "Book returned successfully.") in flashes


def test_mark_book_picked_up_success(app, controller, reservation_row):
    reservation_row["status"] = "reserved"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/mark-picked-up/50", method="POST"):
        response = controller.mark_book_picked_up(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.mark_picked_up.assert_called_once()
    assert ("success", "Book marked as picked up. Student must return it within 15 days.") in flashes


def test_request_renew_success(app, controller, reservation_row):
    reservation_row["status"] = "borrowed"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/request-renew-book/50", method="POST"):
        session["user_id"] = 1
        response = controller.request_renew_book(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.request_renew.assert_called_once_with(50, 1)
    assert ("success", "Renew request sent to admin for approval.") in flashes


def test_approve_renew_adds_15_days(app, controller, reservation_row):
    reservation_row["status"] = "renew_requested"
    reservation_row["due_date"] = "2026-06-30"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/approve-renew-book/50", method="POST"):
        response = controller.approve_renew_book(50)
        flashes = get_flashed_messages(with_categories=True)

    expected_new_date = date(2026, 7, 15)
    controller.reservation_model.approve_renew.assert_called_once_with(50, expected_new_date)
    assert response.status_code == 302
    assert ("success", "Renew request approved. Due date extended by 15 days.") in flashes


def test_reject_renew_success(app, controller, reservation_row):
    reservation_row["status"] = "renew_requested"
    controller.reservation_model.find_by_id.return_value = reservation_row

    with app.test_request_context("/reject-renew-book/50", method="POST"):
        response = controller.reject_renew_book(50)
        flashes = get_flashed_messages(with_categories=True)

    assert response.status_code == 302
    controller.reservation_model.reject_renew.assert_called_once_with(50)
    assert ("success", "Renew request rejected. Student must return the book by the current due date.") in flashes
