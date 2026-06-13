"""
=============================================================
  OOP Concept: INHERITANCE, ENCAPSULATION & POLYMORPHISM
=============================================================
  - Inheritance: User inherits from BaseModel, so it gets find_by_id(), find_all(), delete_by_id() for FREE.
  - Encapsulation: Password is kept private (__password). Outside code cannot access user.__password directly.
    We use a setter method to control how it's changed.
  - Polymorphism: User defines its own 'table' property, which overrides the abstract one from BaseModel.
    Same interface, different behavior = polymorphism.
=============================================================
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel
from app.models.database import Database


class User(BaseModel):
    """
    User Model — represents a single user in our app.

    Inherits from BaseModel:
      - find_by_id(id)
      - find_by(column, value)
      - find_all()
      - count_all()
      - delete_by_id(id)
    """

    # ── Polymorphism: Override the abstract 'table' property ──
    @property
    def table(self):
        """Tell BaseModel which database table to use."""
        return "users"

    # ── Constructor ─────────────────────────────────────────
    def __init__(self, name=None, email=None, password=None, role="user"):
        """
        Create a User object.

        Encapsulation:
          - __password is PRIVATE (double underscore).
          - It can only be set through set_password().
          - This protects the password from accidental access.
        """
        self.name = name
        self.email = email
        self.__password = None
        self.role = role

        # Hash the password if one was provided
        if password:
            self.set_password(password)

    # ── Encapsulation: Password Methods ─────────────────────

    def set_password(self, plain_password):
        """
        Hash and store the password securely.
        This is the ONLY way to set a password — encapsulation!
        """
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        """Check if the given password matches the stored hash."""
        if self.__password is None:
            return False
        return check_password_hash(self.__password, plain_password)


# forgot pass
    def find_by_email(self, email):
        db = Database()
        user = db.fetch_one(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        db.close()
        return user


    def save_reset_otp(self, email, hashed_otp, expiry_time):
        db = Database()
        db.execute(
            """
            UPDATE users
            SET reset_otp = %s,
                reset_otp_expires = %s
            WHERE email = %s
            """,
            (hashed_otp, expiry_time, email)
        )
        db.close()


    def update_password_by_email(self, email, hashed_password):
        db = Database()
        db.execute(
            """
            UPDATE users
            SET password = %s,
                reset_otp = NULL,
                reset_otp_expires = NULL
            WHERE email = %s
            """,
            (hashed_password, email)
        )
        db.close()
    # ── Create: Save a new user to the database ─────────────

    def save(self):
        """Insert this user into the database."""
        db = Database()
        db.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (self.name, self.email, self.__password, self.role),
        )
        db.close()

    # ── Update: Modify an existing user ─────────────────────

    def update(self, user_id, update_password=False):
        """
        Update user in database.
        If update_password=True, the password is also updated.
        """
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET name=%s, email=%s, password=%s, role=%s WHERE id=%s",
                (self.name, self.email, self.__password, self.role, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET name=%s, email=%s, role=%s WHERE id=%s",
                (self.name, self.email, self.role, user_id),
            )
        db.close()

    def update_profile(self, user_id, update_password=False):
        """
        Update profile (name, email, and optionally password).
        Used when a user edits their own profile (no role change).
        """
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                (self.name, self.email, self.__password, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET name=%s, email=%s WHERE id=%s",
                (self.name, self.email, user_id),
            )
        db.close()

    # ── Helper: Check if email is already taken ─────────────

    def email_exists(self, exclude_id=None):
        """
        Check if this user's email is already in the database.
        exclude_id: ignore this user ID (useful when updating).
        """
        db = Database()
        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (self.email, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email = %s", (self.email,)
            )
        db.close()
        return result is not None

    # ── Class Method: Build a User object from DB data ──────

    @classmethod
    def from_db(cls, data):
        """
        Create a User object from a database dictionary.

        @classmethod means you call it on the class itself:
            user = User.from_db(row)
        instead of creating an instance first.
        """
        if data is None:
            return None
        user = cls()
        user.name = data["name"]
        user.email = data["email"]
        user.__password = data["password"]
        user.role = data["role"]
        return user

    # ── Magic Method: String representation ─────────────────

    def __str__(self):
        """
        Magic method: defines what print(user) shows.
        This is Python's way of polymorphism — every class
        can define its own __str__ behavior.
        """
        return f"User(name={self.name}, email={self.email}, role={self.role})"

    def __repr__(self):
        """Developer-friendly representation for debugging."""
        return f"<User email={self.email}>"
    
    def find_all(self, order_by="id"):
        db = Database()
        results = db.fetch_all(
            f"SELECT * FROM {self.table} WHERE role != 'admin' ORDER BY {order_by}"
        )
        db.close()
        return results