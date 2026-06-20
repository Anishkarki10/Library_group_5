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
        image=None,
        isbn=None,
        publisher=None,
        year=None,
        edition=None,
        pages=None,
        description=None
    ):
        self.title = title
        self.author = author
        self.genre = genre
        self.total = total
        self.available_count = available_count
        self.location = location
        self.image = image
        self.isbn = isbn
        self.publisher = publisher
        self.year = year
        self.edition = edition
        self.pages = pages
        self.description = description

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

    def save(
        self,
        title=None,
        author=None,
        genre=None,
        total=None,
        available_count=None,
        location=None,
        image=None,
        isbn=None,
        publisher=None,
        year=None,
        edition=None,
        pages=None,
        description=None
    ):
        title = title if title is not None else self.title
        author = author if author is not None else self.author
        genre = genre if genre is not None else self.genre
        total = total if total is not None else self.total
        available_count = available_count if available_count is not None else self.available_count
        location = location if location is not None else self.location
        image = image if image is not None else self.image
        isbn = isbn if isbn is not None else self.isbn
        publisher = publisher if publisher is not None else self.publisher
        year = year if year is not None else self.year
        edition = edition if edition is not None else self.edition
        pages = pages if pages is not None else self.pages
        description = description if description is not None else self.description

        db = Database()
        db.execute("""
            INSERT INTO books
            (
                title,
                author,
                genre,
                total,
                available_count,
                location,
                image,
                isbn,
                publisher,
                year,
                edition,
                pages,
                description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            title,
            author,
            genre,
            total,
            available_count,
            location,
            image,
            isbn,
            publisher,
            year,
            edition,
            pages,
            description
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
            WHERE id = %s
            AND available_count > 0
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

    def update(
        self,
        book_id,
        title,
        author,
        genre,
        total,
        available_count,
        location,
        image=None,
        isbn=None,
        publisher=None,
        year=None,
        edition=None,
        pages=None,
        description=None
    ):
        db = Database()

        if image:
            db.execute("""
                UPDATE books
                SET title = %s,
                    author = %s,
                    genre = %s,
                    total = %s,
                    available_count = %s,
                    location = %s,
                    image = %s,
                    isbn = %s,
                    publisher = %s,
                    year = %s,
                    edition = %s,
                    pages = %s,
                    description = %s
                WHERE id = %s
            """, (
                title,
                author,
                genre,
                total,
                available_count,
                location,
                image,
                isbn,
                publisher,
                year,
                edition,
                pages,
                description,
                book_id
            ))
        else:
            db.execute("""
                UPDATE books
                SET title = %s,
                    author = %s,
                    genre = %s,
                    total = %s,
                    available_count = %s,
                    location = %s,
                    isbn = %s,
                    publisher = %s,
                    year = %s,
                    edition = %s,
                    pages = %s,
                    description = %s
                WHERE id = %s
            """, (
                title,
                author,
                genre,
                total,
                available_count,
                location,
                isbn,
                publisher,
                year,
                edition,
                pages,
                description,
                book_id
            ))

        db.close()