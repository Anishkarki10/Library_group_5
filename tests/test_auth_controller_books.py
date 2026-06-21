import io
from unittest.mock import patch
from flask import get_flashed_messages, session


def test_allowed_file(controller):
    assert controller.allowed_file("cover.jpg") is True
    assert controller.allowed_file("cover.png") is True
    assert controller.allowed_file("cover.webp") is True
    assert controller.allowed_file("cover.pdf") is False
    assert controller.allowed_file("cover") is False


def test_home_splits_reservations(app, controller):
    controller.ebook_model.get_all.return_value = ["ebook"]
    controller.book_model.get_all.return_value = ["book"]
    controller.reservation_model.get_user_reservations.return_value = [
        {"id":1, "status":"borrowed"}, {"id":2, "status":"returned"}, {"id":3, "status":"cancelled"}
    ]
    with patch("app.controllers.auth.render_template", return_value="home_page") as mock_render:
        with app.test_request_context("/"):
            session["user_id"] = 1
            session["reservation_success"] = {"title":"Book", "location":"Shelf A"}
            assert controller.home() == "home_page"
    kwargs = mock_render.call_args.kwargs
    assert kwargs["reservations"] == [{"id":1, "status":"borrowed"}]
    assert kwargs["reading_history"] == [{"id":2, "status":"returned"}]
    assert kwargs["cancelled_reservations"] == [{"id":3, "status":"cancelled"}]
    assert kwargs["reservation_success"] == {"title":"Book", "location":"Shelf A"}


def test_add_book_missing_required(app, controller):
    with app.test_request_context("/add-book", method="POST", data={}):
        response = controller.add_book()
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.book_model.save.assert_not_called()
    assert ("danger", "Title, author, genre, total copies, and location are required.") in flashes


def test_add_book_success_no_image(app, controller):
    data = {"title":"Atomic Habits", "author":"James Clear", "genre":"Personal Development", "total":"5", "location":"Shelf P-01", "isbn":"123", "publisher":"Avery", "year":"2018", "edition":"1st", "pages":"320", "description":"Habit book"}
    with app.test_request_context("/add-book", method="POST", data=data):
        response = controller.add_book()
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    args = controller.book_model.save.call_args.args
    assert args[0] == "Atomic Habits"
    assert args[3] == 5
    assert args[4] == 5
    assert args[6] is None
    assert args[12] == "Habit book"
    assert ("success", "Book added successfully.") in flashes


def test_add_book_success_with_image(app, controller):
    data = {"title":"Book", "author":"Author", "genre":"Genre", "total":"2", "location":"Shelf A", "image": (io.BytesIO(b"fake"), "cover.jpg")}
    with app.test_request_context("/add-book", method="POST", data=data, content_type="multipart/form-data"):
        response = controller.add_book()
    assert response.status_code == 302
    assert controller.book_model.save.call_args.args[6] == "cover.jpg"


def test_delete_book_not_found(app, controller):
    controller.book_model.find_by_id.return_value = None
    with app.test_request_context("/delete-book/10", method="POST"):
        response = controller.delete_book(10)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.book_model.delete.assert_not_called()
    assert ("danger", "Book not found.") in flashes


def test_delete_book_success(app, controller, book_row):
    controller.book_model.find_by_id.return_value = book_row
    with app.test_request_context("/delete-book/10", method="POST"):
        response = controller.delete_book(10)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.book_model.delete.assert_called_once_with(10)
    assert ("success", "Book deleted successfully.") in flashes


def test_edit_book_success(app, controller):
    data = {"title":"Updated", "author":"Author", "genre":"Genre", "total":"4", "available_count":"2", "location":"Shelf B", "isbn":"123", "publisher":"Pub", "year":"2024", "edition":"2nd", "pages":"250", "description":"Updated"}
    with app.test_request_context("/edit-book/10", method="POST", data=data):
        response = controller.edit_book(10)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    args = controller.book_model.update.call_args.args
    assert args[0] == 10
    assert args[1] == "Updated"
    assert args[4] == 4
    assert args[5] == 2
    assert args[7] is None
    assert ("success", "Book updated successfully.") in flashes
