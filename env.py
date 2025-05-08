import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")
DATABASE_PATH = os.getenv("DATABASE_PATH")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
