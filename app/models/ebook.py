from app.models.database import Database


class EBook:
    def get_all(self):
        db = Database()
        ebooks = db.fetch_all("""
            SELECT *
            FROM ebooks
            ORDER BY id DESC
        """)
        db.close()
        return ebooks

    def find_by_id(self, ebook_id):
        db = Database()
        ebook = db.fetch_one("""
            SELECT *
            FROM ebooks
            WHERE id = %s
        """, (ebook_id,))
        db.close()
        return ebook

    def save(self, title, author, category, pages, file_size, description, pdf_file, cover_image):
        db = Database()
        db.execute("""
            INSERT INTO ebooks
            (title, author, category, pages, file_size, description, pdf_file, cover_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            title,
            author,
            category,
            pages,
            file_size,
            description,
            pdf_file,
            cover_image
        ))
        db.close()

    def update(self, ebook_id, title, author, category, pages, file_size, description, pdf_file=None, cover_image=None):
        db = Database()

        if pdf_file and cover_image:
            db.execute("""
                UPDATE ebooks
                SET title = %s,
                    author = %s,
                    category = %s,
                    pages = %s,
                    file_size = %s,
                    description = %s,
                    pdf_file = %s,
                    cover_image = %s
                WHERE id = %s
            """, (
                title,
                author,
                category,
                pages,
                file_size,
                description,
                pdf_file,
                cover_image,
                ebook_id
            ))

        elif pdf_file:
            db.execute("""
                UPDATE ebooks
                SET title = %s,
                    author = %s,
                    category = %s,
                    pages = %s,
                    file_size = %s,
                    description = %s,
                    pdf_file = %s
                WHERE id = %s
            """, (
                title,
                author,
                category,
                pages,
                file_size,
                description,
                pdf_file,
                ebook_id
            ))

        elif cover_image:
            db.execute("""
                UPDATE ebooks
                SET title = %s,
                    author = %s,
                    category = %s,
                    pages = %s,
                    file_size = %s,
                    description = %s,
                    cover_image = %s
                WHERE id = %s
            """, (
                title,
                author,
                category,
                pages,
                file_size,
                description,
                cover_image,
                ebook_id
            ))

        else:
            db.execute("""
                UPDATE ebooks
                SET title = %s,
                    author = %s,
                    category = %s,
                    pages = %s,
                    file_size = %s,
                    description = %s
                WHERE id = %s
            """, (
                title,
                author,
                category,
                pages,
                file_size,
                description,
                ebook_id
            ))

        db.close()

    def delete(self, ebook_id):
        db = Database()
        db.execute("""
            DELETE FROM ebooks
            WHERE id = %s
        """, (ebook_id,))
        db.close()