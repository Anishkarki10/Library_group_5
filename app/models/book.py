from app.models.database import Database


class Book:
    def __init__(
        self,
        title=None,
        author=None,
        genre=None,
        total=None,
        available_count=None,
        location=None,
        image=None
    ):
        self.title = title
        self.author = author
        self.genre = genre
        self.total = total
        self.available_count = available_count
        self.location = location
        self.image = image

    def get_all(self):
        db = Database()
        books = db.fetch_all("""
            SELECT *
            FROM books
            ORDER BY id DESC
        """)
        db.close()
        return books

    def find_by_id(self, book_id):
        db = Database()
        book = db.fetch_one("""
            SELECT *
            FROM books
            WHERE id = %s
        """, (book_id,))
        db.close()
        return book

    def save(self):
        db = Database()
        db.execute("""
            INSERT INTO books
            (title, author, genre, total, available_count, location, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            self.title,
            self.author,
            self.genre,
            self.total,
            self.available_count,
            self.location,
            self.image
        ))
        db.close()

    def delete(self, book_id):
        db = Database()
        db.execute("""
            DELETE FROM books
            WHERE id = %s
        """, (book_id,))
        db.close()
    
    def decrease_available(self, book_id):
        db = Database()
        db.execute("""
            UPDATE books
            SET available_count = available_count - 1
            WHERE id = %s AND available_count > 0
        """, (book_id,))
        db.close()
    
    def increase_available(self, book_id):
        db = Database()
        db.execute("""
            UPDATE books
            SET available_count = available_count + 1
            WHERE id = %s
        """, (book_id,))
        db.close()