import sqlite3
import logging
from hashlib import sha256
from env import ADMIN_USERNAME, ADMIN_PASSWORD, DATABASE_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("user_system.log"),
        logging.StreamHandler()
    ]
)

class User:
    def __init__(self, db_name=DATABASE_PATH):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_user_table()
        self._ensure_admin_exists()

    def _hash_password(self, password):
        return sha256(password.encode()).hexdigest()

    def _create_user_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS USER (
                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                Password TEXT NOT NULL,
                FullName TEXT,
                Qualification TEXT,
                DOB DATE,
                IsAdmin BOOLEAN DEFAULT 0
            )
        """)
        self.conn.commit()
        logging.info("User table ensured in database.")

    def _ensure_admin_exists(self):
        admin_username = ADMIN_USERNAME
        admin_password = self._hash_password(ADMIN_PASSWORD)
        self.cursor.execute("SELECT * FROM USER WHERE Username = ? AND IsAdmin = 1", (admin_username,))
        if not self.cursor.fetchone():
            self.cursor.execute("""
                INSERT INTO USER (Username, Password, FullName, Qualification, DOB, IsAdmin)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (admin_username, admin_password, "System Administrator", "Admin", "1970-01-01"))
            self.conn.commit()
            logging.info("Default admin account created.")
        else:
            logging.info("Admin account already exists.")

    def register(self, username, password, full_name, qualification, dob):
        hash_password = self._hash_password(password)
        if username.lower() == "admin":
            logging.warning("Cannot register admin user.")
            return
        try:
            self.cursor.execute("""
                INSERT INTO USER (Username, Password, FullName, Qualification, DOB)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hash_password, full_name, qualification, dob))
            self.conn.commit()
            logging.info(f"User '{username}' registered successfully.")
        except sqlite3.IntegrityError:
            logging.warning(f"Registration failed: Username '{username}' already exists.")

    def login(self, username, password):
        hash_password = self._hash_password(password)
        self.cursor.execute("""
            SELECT * FROM USER WHERE Username = ? AND Password = ?
        """, (username, hash_password))
        user = self.cursor.fetchone()
        if user:
            role = "Admin" if user["IsAdmin"] == 1 else "User"
            logging.info(f"{role} login successful for user '{username}'.")
            return user, role
        else:
            logging.warning(f"Login failed for user '{username}'. Incorrect credentials.")
            return None, None

    def remove_user(self, username):
        if username.lower() == "admin":
            logging.warning("Attempt to delete admin blocked.")
            return
        self.cursor.execute("""
            DELETE FROM USER WHERE Username = ?
        """, (username,))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            logging.info(f"User '{username}' removed successfully.")
        else:
            logging.warning(f"No user found with username '{username}'.")

    def close(self):
        self.conn.close()
        logging.info("Database connection closed.")
