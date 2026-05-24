"""
=============================================================
  OOP Concept: INHERITANCE & ENCAPSULATION (Base Controller)
=============================================================
  - This is the PARENT class for all controllers.
  - It provides shared helper methods that every controller needs (like getting form data or checking login).
  - Child classes (AuthController, UserController) INHERIT all these methods and can also add their own.
=============================================================
"""

from flask import session, flash, redirect, url_for, request


class BaseController:
    """
    Base Controller — parent class for all controllers.

    Provides common functionality:
      - get_form_data(): safely read form inputs
      - is_logged_in(): check if user is logged in
      - get_current_user_id(): get logged-in user's ID
      - flash_and_redirect(): show message and redirect
    """

    def get_form_data(self, *fields):
        """
        Safely get multiple form fields at once.

        Usage:
            name, email = self.get_form_data('name', 'email')

        Returns stripped strings (no extra spaces).
        """
        return tuple(request.form.get(field, "").strip() for field in fields)

    def is_logged_in(self):
        """Check if a user is currently logged in."""
        return "user_id" in session

    def get_current_user_id(self):
        """Get the logged-in user's ID from session."""
        return session.get("user_id")

    def get_current_role(self):
        """Get the logged-in user's role from session."""
        return session.get("role")

    def flash_and_redirect(self, message, category, endpoint):
        """Show a flash message and redirect to a page."""
        flash(message, category)
        return redirect(url_for(endpoint))
