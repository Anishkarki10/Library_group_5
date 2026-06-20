from datetime import datetime, timedelta
from app.models.database import Database


class Reservation:
    def create(self, user_id, book_id, due_date):
        db = Database()
        db.execute("""
            INSERT INTO reservations (user_id, book_id, status, due_date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, book_id, "reserved", due_date))
        db.close()

    def already_reserved(self, user_id, book_id):
        db = Database()
        result = db.fetch_one("""
            SELECT *
            FROM reservations
            WHERE user_id = %s
            AND book_id = %s
            AND status IN ('reserved', 'borrowed', 'cancel_requested', 'renew_requested')
        """, (user_id, book_id))
        db.close()
        return result is not None

    def get_user_reservations(self, user_id):
        db = Database()
        reservations = db.fetch_all("""
            SELECT 
                reservations.id,
                reservations.user_id,
                reservations.book_id,
                reservations.status,
                reservations.reserved_at,
                reservations.due_date,
                reservations.returned_at,
                books.title,
                books.author,
                books.genre,
                books.location,
                books.image
            FROM reservations
            JOIN books ON reservations.book_id = books.id
            WHERE reservations.user_id = %s
            ORDER BY reservations.id DESC
        """, (user_id,))
        db.close()
        return reservations

    def get_all_reservations(self):
        db = Database()
        reservations = db.fetch_all("""
            SELECT 
                reservations.id,
                reservations.user_id,
                reservations.book_id,
                reservations.status,
                reservations.reserved_at,
                reservations.due_date,
                reservations.returned_at,
                users.name AS student_name,
                users.email AS student_email,
                books.title AS book_title,
                books.author AS book_author,
                books.location AS book_location
            FROM reservations
            JOIN users ON reservations.user_id = users.id
            JOIN books ON reservations.book_id = books.id
            ORDER BY reservations.id DESC
        """)
        db.close()
        return reservations

    def find_by_id(self, reservation_id):
        db = Database()
        reservation = db.fetch_one("""
            SELECT 
                reservations.id,
                reservations.user_id,
                reservations.book_id,
                reservations.status,
                reservations.reserved_at,
                reservations.due_date,
                reservations.returned_at,
                users.name AS student_name,
                users.email AS student_email,
                books.title AS book_title,
                books.author AS book_author,
                books.location AS book_location
            FROM reservations
            JOIN users ON reservations.user_id = users.id
            JOIN books ON reservations.book_id = books.id
            WHERE reservations.id = %s
        """, (reservation_id,))
        db.close()
        return reservation

    # ── Student Cancel Request ───────────────────────────────

    def request_cancel(self, reservation_id, user_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'cancel_requested'
            WHERE id = %s
            AND user_id = %s
            AND status IN ('reserved', 'borrowed')
        """, (reservation_id, user_id))
        db.close()

    # ── Admin Approve Cancel ────────────────────────────────

    def approve_cancel(self, reservation_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'cancelled',
                returned_at = NOW()
            WHERE id = %s
            AND status = 'cancel_requested'
        """, (reservation_id,))
        db.close()

    # ── Admin Reject Cancel ─────────────────────────────────

    def reject_cancel(self, reservation_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'reserved'
            WHERE id = %s
            AND status = 'cancel_requested'
        """, (reservation_id,))
        db.close()

    # ── Return Book ─────────────────────────────────────────

    def mark_returned(self, reservation_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'returned',
                returned_at = NOW()
            WHERE id = %s
            AND status IN ('reserved', 'borrowed', 'renew_requested')
        """, (reservation_id,))
        db.close()

    # ── Admin Mark Picked Up ────────────────────────────────

    def mark_picked_up(self, reservation_id, due_date):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'borrowed',
                due_date = %s
            WHERE id = %s
            AND status = 'reserved'
        """, (due_date, reservation_id))
        db.close()

    # ── Student Request Renew / Extend Time ─────────────────

    def request_renew(self, reservation_id, user_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'renew_requested'
            WHERE id = %s
            AND user_id = %s
            AND status = 'borrowed'
        """, (reservation_id, user_id))
        db.close()

    # ── Admin Approve Renew / Extend Time By 15 Days ─────────

    def approve_renew(self, reservation_id, new_due_date=None):
        db = Database()

        if new_due_date is None:
            reservation = self.find_by_id(reservation_id)

            if reservation and reservation.get("due_date"):
                current_due_date = reservation["due_date"]

                if isinstance(current_due_date, str):
                    current_due_date = datetime.strptime(current_due_date, "%Y-%m-%d").date()

                new_due_date = current_due_date + timedelta(days=15)
            else:
                new_due_date = datetime.now().date() + timedelta(days=15)

        db.execute("""
            UPDATE reservations
            SET status = 'borrowed',
                due_date = %s
            WHERE id = %s
            AND status = 'renew_requested'
        """, (new_due_date, reservation_id))

        db.close()

    # ── Admin Reject Renew ──────────────────────────────────

    def reject_renew(self, reservation_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'borrowed'
            WHERE id = %s
            AND status = 'renew_requested'
        """, (reservation_id,))
        db.close()

    # ── Direct Cancel, optional use ─────────────────────────

    def cancel_reservation(self, reservation_id):
        db = Database()
        db.execute("""
            UPDATE reservations
            SET status = 'cancelled',
                returned_at = NOW()
            WHERE id = %s
            AND status IN ('reserved', 'borrowed', 'cancel_requested', 'renew_requested')
        """, (reservation_id,))
        db.close()