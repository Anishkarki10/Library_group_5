"""
=============================================================
  OOP Concept: INHERITANCE, ENCAPSULATION & POLYMORPHISM
=============================================================
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel
from app.models.database import Database


class User(BaseModel):
    """
    User Model — represents a single user in our app.
    """

    @property
    def table(self):
        """Tell BaseModel which database table to use."""
        return "users"

    def __init__(self, name=None, email=None, password=None, role="user"):
        self.name = name
        self.email = email
        self.__password = None
        self.role = role

        if password:
            self.set_password(password)

    # ── Password Methods ─────────────────────────────

    def set_password(self, plain_password):
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        if self.__password is None:
            return False
        return check_password_hash(self.__password, plain_password)

    # ── Create User ─────────────────────────────────

    def save(self):
        db = Database()
        db.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """,
            (self.name, self.email, self.__password, self.role)
        )
        db.close()

    # ── Update User ─────────────────────────────────

    def update(self, user_id, update_password=False):
        db = Database()

        if update_password:
            db.execute(
                """
                UPDATE users
                SET name = %s, email = %s, password = %s, role = %s
                WHERE id = %s
                """,
                (self.name, self.email, self.__password, self.role, user_id)
            )
        else:
            db.execute(
                """
                UPDATE users
                SET name = %s, email = %s, role = %s
                WHERE id = %s
                """,
                (self.name, self.email, self.role, user_id)
            )

        db.close()

    def update_profile(self, user_id, update_password=False):
        db = Database()

        if update_password:
            db.execute(
                """
                UPDATE users
                SET name = %s, email = %s, password = %s
                WHERE id = %s
                """,
                (self.name, self.email, self.__password, user_id)
            )
        else:
            db.execute(
                """
                UPDATE users
                SET name = %s, email = %s
                WHERE id = %s
                """,
                (self.name, self.email, user_id)
            )

        db.close()

    # ── Email Check ─────────────────────────────────

    def email_exists(self, exclude_id=None):
        db = Database()

        if exclude_id:
            result = db.fetch_one(
                """
                SELECT id FROM users
                WHERE email = %s AND id != %s
                """,
                (self.email, exclude_id)
            )
        else:
            result = db.fetch_one(
                """
                SELECT id FROM users
                WHERE email = %s
                """,
                (self.email,)
            )

        db.close()
        return result is not None

    # ── Forgot Password OTP Methods ─────────────────

    def find_by_email(self, email):
        db = Database()
        user = db.fetch_one(
            """
            SELECT * FROM users
            WHERE email = %s
            """,
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

    # ── Custom Find All ─────────────────────────────

    def find_all(self, order_by="id"):
        db = Database()
        results = db.fetch_all(
            f"""
            SELECT * FROM {self.table}
            WHERE role != 'admin'
            ORDER BY {order_by}
            """
        )
        db.close()
        return results

    # ── Convert DB Row To Object ────────────────────

    @classmethod
    def from_db(cls, data):
        if data is None:
            return None

        user = cls()
        user.name = data["name"]
        user.email = data["email"]
        user.__password = data["password"]
        user.role = data["role"]

        return user

    # ── String Representation ──────────────────────

    def __str__(self):
        return f"User(name={self.name}, email={self.email}, role={self.role})"

    def __repr__(self):
        return f"<User email={self.email}>"