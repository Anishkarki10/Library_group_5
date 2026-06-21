import io
from flask import get_flashed_messages


def test_allowed_pdf_and_image(controller):
    assert controller.allowed_pdf("book.pdf") is True
    assert controller.allowed_pdf("book.docx") is False
    assert controller.allowed_image("cover.jpg") is True
    assert controller.allowed_image("cover.webp") is True
    assert controller.allowed_image("cover.pdf") is False


def test_get_file_size_text(controller):
    fake_file = io.BytesIO(b"a" * 2048)
    assert controller.get_file_size_text(fake_file) == "2.0 KB"


def test_add_ebook_missing_pdf(app, controller):
    data = {"title":"EBook", "author":"Author", "category":"Category"}
    with app.test_request_context("/add-ebook", method="POST", data=data):
        response = controller.add_ebook()
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.ebook_model.save.assert_not_called()
    assert ("danger", "Title, author, category, and PDF file are required.") in flashes


def test_add_ebook_rejects_non_pdf(app, controller):
    data = {"title":"EBook", "author":"Author", "category":"Category", "pdf_file": (io.BytesIO(b"bad"), "ebook.txt")}
    with app.test_request_context("/add-ebook", method="POST", data=data, content_type="multipart/form-data"):
        response = controller.add_ebook()
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.ebook_model.save.assert_not_called()
    assert ("danger", "Only PDF files are allowed for e-books.") in flashes


def test_add_ebook_success(app, controller):
    data = {"title":"Confidence Guide", "author":"Author", "category":"Personality", "pages":"30", "description":"Demo", "pdf_file": (io.BytesIO(b"%PDF-1.4"), "confidence.pdf"), "cover_image": (io.BytesIO(b"img"), "confidence.jpg")}
    with app.test_request_context("/add-ebook", method="POST", data=data, content_type="multipart/form-data"):
        response = controller.add_ebook()
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    args = controller.ebook_model.save.call_args.args
    assert args[0] == "Confidence Guide"
    assert args[3] == 30
    assert args[6] == "confidence.pdf"
    assert args[7] == "confidence.jpg"
    assert ("success", "E-book added successfully.") in flashes


def test_edit_ebook_not_found(app, controller):
    controller.ebook_model.find_by_id.return_value = None
    with app.test_request_context("/edit-ebook/1", method="POST"):
        response = controller.edit_ebook(1)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    assert ("danger", "E-book not found.") in flashes


def test_edit_ebook_success_without_new_files(app, controller):
    controller.ebook_model.find_by_id.return_value = {"id":1, "file_size":"1.0 MB", "pdf_file":"old.pdf", "cover_image":"old.jpg"}
    data = {"title":"Updated", "author":"Author", "category":"Category", "pages":"50", "description":"Updated"}
    with app.test_request_context("/edit-ebook/1", method="POST", data=data):
        response = controller.edit_ebook(1)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.ebook_model.update.assert_called_once_with(1, "Updated", "Author", "Category", 50, "1.0 MB", "Updated", None, None)
    assert ("success", "E-book updated successfully.") in flashes


def test_delete_ebook_success(app, controller):
    controller.ebook_model.find_by_id.return_value = {"id":1, "pdf_file":"ebook.pdf", "cover_image":"cover.jpg"}
    with app.test_request_context("/delete-ebook/1", method="POST"):
        response = controller.delete_ebook(1)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.ebook_model.delete.assert_called_once_with(1)
    assert ("success", "E-book deleted successfully.") in flashes
