from unittest.mock import MagicMock, patch
from flask import get_flashed_messages


@patch("app.controllers.auth.render_template")
def test_dashboard_loads_data(mock_render, app, controller):
    mock_render.return_value = "dashboard_page"
    controller.user_model.find_all.return_value = ["u"]
    controller.book_model.get_all.return_value = ["b"]
    controller.reservation_model.get_all_reservations.return_value = ["r"]
    controller.ebook_model.get_all.return_value = ["e"]
    with app.test_request_context("/dashboard"):
        result = controller.dashboard()
    assert result == "dashboard_page"
    kwargs = mock_render.call_args.kwargs
    assert kwargs["users"] == ["u"]
    assert kwargs["books"] == ["b"]
    assert kwargs["reservations"] == ["r"]
    assert kwargs["ebooks"] == ["e"]


@patch("app.controllers.auth.render_template")
def test_add_user_get(mock_render, app, controller):
    mock_render.return_value = "add_page"
    with app.test_request_context("/add-user", method="GET"):
        assert controller.add_user() == "add_page"
    mock_render.assert_called_once_with("addUser.html")


@patch("app.controllers.auth.render_template")
def test_add_user_missing_fields(mock_render, app, controller):
    mock_render.return_value = "add_page"
    with app.test_request_context("/add-user", method="POST", data={}):
        result = controller.add_user()
        flashes = get_flashed_messages(with_categories=True)
    assert result == "add_page"
    assert ("danger", "All fields are required.") in flashes


@patch("app.controllers.auth.User")
def test_add_user_success(mock_user_class, app, controller):
    fake_user = MagicMock(); fake_user.email_exists.return_value = False
    mock_user_class.return_value = fake_user
    data = {"name":"Bob", "email":"bob@test.com", "password":"secret1", "confirm_password":"secret1", "role":"user"}
    with app.test_request_context("/add-user", method="POST", data=data):
        response = controller.add_user()
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    assert "/dashboard" in response.location
    fake_user.save.assert_called_once()
    assert ("success", "User added successfully.") in flashes


@patch("app.controllers.auth.User.from_db")
@patch("app.controllers.auth.render_template")
def test_edit_user_get(mock_render, mock_from_db, app, controller, user_row):
    mock_render.return_value = "edit_page"
    controller.user_model.find_by_id.return_value = user_row
    mock_from_db.return_value = MagicMock()
    with app.test_request_context("/edit/1", method="GET"):
        assert controller.editUsers(1) == "edit_page"
    mock_render.assert_called_once_with("editUser.html", user=user_row)


@patch("app.controllers.auth.User.from_db")
def test_edit_user_success(mock_from_db, app, controller, user_row):
    user_obj = MagicMock()
    mock_from_db.return_value = user_obj
    controller.user_model.find_by_id.return_value = user_row
    data = {"name":"Updated", "email":"updated@test.com", "role":"user"}
    with app.test_request_context("/edit/1", method="POST", data=data):
        response = controller.editUsers(1)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    assert "/dashboard" in response.location
    user_obj.update.assert_called_once_with(user_id=1, update_password=False)
    assert ("success", "User updated successfully.") in flashes


def test_delete_user_blocks_admin(app, controller):
    controller.user_model.find_by_id.return_value = {"id": 1, "role": "admin"}
    with app.test_request_context("/delete/1", method="POST"):
        response = controller.deleteUser(1)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.user_model.delete_by_id.assert_not_called()
    assert ("danger", "Admin cannot be deleted.") in flashes


def test_delete_user_success(app, controller):
    controller.user_model.find_by_id.return_value = {"id": 3, "role": "user"}
    with app.test_request_context("/delete/3", method="POST"):
        response = controller.deleteUser(3)
        flashes = get_flashed_messages(with_categories=True)
    assert response.status_code == 302
    controller.user_model.delete_by_id.assert_called_once_with(3)
    assert ("success", "User deleted successfully.") in flashes
