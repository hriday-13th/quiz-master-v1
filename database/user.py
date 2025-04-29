import sqlite3
import logging
from hashlib import sha256

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("user_system.log"),
        logging.StreamHandler()
    ]
)

class User:
    def __init__(self, db_name="quizmaster.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_user_table()
        self._ensure_admin_exists()

    def _create_user_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                qualification TEXT,
                dob TEXT,
                is_admin INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
        logging.info("User table ensured in database.")

    def _hash_password(self, password):
        return sha256(password.encode()).hexdigest()

    def _ensure_admin_exists(self):
        admin_username = "admin"
        admin_password = self._hash_password("admin123")
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND is_admin = 1", (admin_username,))
        if not self.cursor.fetchone():
            self.cursor.execute("""
                INSERT INTO users (username, password, full_name, qualification, dob, is_admin)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (admin_username, admin_password, "System Administrator", "Admin", "1970-01-01"))
            self.conn.commit()
            logging.info("Default admin account created.")
        else:
            logging.info("Admin account already exists.")

    def register(self, username, password, full_name, qualification, dob):
        if username.lower() == "admin":
            logging.warning("Cannot register admin user.")
            return
        try:
            hashed_password = self._hash_password(password)
            self.cursor.execute("""
                INSERT INTO users (username, password, full_name, qualification, dob)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_password, full_name, qualification, dob))
            self.conn.commit()
            logging.info(f"User '{username}' registered successfully.")
        except sqlite3.IntegrityError:
            logging.warning(f"Registration failed: Username '{username}' already exists.")

    def login(self, username, password):
        hashed_password = self._hash_password(password)
        self.cursor.execute("""
            SELECT * FROM users WHERE username = ? AND password = ?
        """, (username, hashed_password))
        user = self.cursor.fetchone()
        if user:
            role = "Admin" if user[6] == 1 else "User"
            logging.info(f"{role} login successful for user '{username}'.")
            return user
        else:
            logging.warning(f"Login failed for user '{username}'. Incorrect credentials.")
            return None

    def remove_user(self, username):
        if username.lower() == "admin":
            logging.warning("Attempt to delete admin blocked.")
            return
        self.cursor.execute("""
            DELETE FROM users WHERE username = ?
        """, (username,))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            logging.info(f"User '{username}' removed successfully.")
        else:
            logging.warning(f"No user found with username '{username}'.")

    def close(self):
        self.conn.close()
        logging.info("Database connection closed.")
