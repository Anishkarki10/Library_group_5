import pymysql
import config


class Database:
    def __init__(self):
        """Open a database connection when object is created."""
        try:
            self.__connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
            )
            print("Database connected successfully!")
        except pymysql.MySQLError as e:
            print("Database connection failed!")
            print("Error:", e)

    def fetch_one(self, query, params=None):
        """Run a query and return ONE result."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        """Run a query and return ALL results."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute(self, query, params=None):
        """Run INSERT, UPDATE, DELETE, CREATE, ALTER queries."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        self.__connection.commit()
        cursor.close()

    def close(self):
        """Close the database connection."""
        self.__connection.close()

    @staticmethod
    def create_tables():
        """
        Create database tables if they don't exist.
        Also adds OTP reset columns if they are missing.
        """
        db = Database()

        # ── Users Table ─────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Add forgot-password OTP columns safely ──
        try:
            db.execute("""
                ALTER TABLE users
                ADD COLUMN reset_otp VARCHAR(255)
            """)
            print("reset_otp column added successfully.")
        except Exception:
            print("reset_otp column already exists or could not be added.")

        try:
            db.execute("""
                ALTER TABLE users
                ADD COLUMN reset_otp_expires DATETIME
            """)
            print("reset_otp_expires column added successfully.")
        except Exception:
            print("reset_otp_expires column already exists or could not be added.")

        # ── Books Table ─────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                author VARCHAR(150) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                total INT NOT NULL,
                available_count INT NOT NULL,
                location VARCHAR(100) NOT NULL,
                image VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Reservations Table ──────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'reserved',
                reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                returned_at DATETIME,

                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)

        # ── Orders Table ────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Products Table ──────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Create default admin if not exists ──────
        admin = db.fetch_one(
            "SELECT * FROM users WHERE email = %s",
            ("admin@admin.com",)
        )

        if not admin:
            from werkzeug.security import generate_password_hash

            db.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    "Admin",
                    "admin@admin.com",
                    generate_password_hash("admin123"),
                    "admin"
                )
            )

            print("Default admin created successfully.")

        db.close()