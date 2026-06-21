from datetime import date
from unittest.mock import MagicMock, patch
from app.models.user import User
from app.models.book import Book
from app.models.ebook import EBook
from app.models.reservation import Reservation


def test_user_password_hash_and_check():
    user = User(name="Alice", email="a@test.com", password="secret1", role="user")
    assert user.check_password("secret1") is True
    assert user.check_password("wrong") is False


def test_user_from_db():
    data = {"name":"Bob", "email":"b@test.com", "password":"hashed", "role":"user"}
    user = User.from_db(data)
    assert user.name == "Bob"
    assert user.email == "b@test.com"
    assert user.role == "user"


@patch("app.models.book.Database")
def test_book_save_runs_insert(mock_db_class):
    db = MagicMock(); mock_db_class.return_value = db
    Book().save("Title","Author","Genre",5,5,"Shelf A","cover.jpg","123","Pub","2024","1st",200,"Desc")
    db.execute.assert_called_once()
    db.close.assert_called_once()


@patch("app.models.book.Database")
def test_book_update_without_image(mock_db_class):
    db = MagicMock(); mock_db_class.return_value = db
    Book().update(1,"Title","Author","Genre",5,4,"Shelf A",None,"123","Pub","2024","1st",200,"Desc")
    query = db.execute.call_args.args[0]
    assert "UPDATE books" in query
    assert "image = %s" not in query
    db.close.assert_called_once()


@patch("app.models.ebook.Database")
def test_ebook_save_runs_insert(mock_db_class):
    db = MagicMock(); mock_db_class.return_value = db
    EBook().save("Title","Author","Cat",30,"1 MB","Desc","file.pdf","cover.jpg")
    db.execute.assert_called_once()
    db.close.assert_called_once()


@patch("app.models.ebook.Database")
def test_ebook_update_without_new_files(mock_db_class):
    db = MagicMock(); mock_db_class.return_value = db
    EBook().update(1,"Title","Author","Cat",30,"1 MB","Desc",None,None)
    query = db.execute.call_args.args[0]
    assert "UPDATE ebooks" in query
    assert "pdf_file = %s" not in query
    assert "cover_image = %s" not in query
    db.close.assert_called_once()


@patch("app.models.reservation.Database")
def test_reservation_already_reserved_true(mock_db_class):
    db = MagicMock(); db.fetch_one.return_value = {"id":1}; mock_db_class.return_value = db
    assert Reservation().already_reserved(1, 10) is True
    db.fetch_one.assert_called_once()
    db.close.assert_called_once()


@patch("app.models.reservation.Database")
def test_reservation_approve_renew_given_date(mock_db_class):
    db = MagicMock(); mock_db_class.return_value = db
    Reservation().approve_renew(50, date(2026,7,15))
    db.execute.assert_called_once()
    assert db.execute.call_args.args[1] == (date(2026,7,15), 50)
    db.close.assert_called_once()
