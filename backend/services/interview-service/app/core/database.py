import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


# Interview Service directory
SERVICE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(SERVICE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is missing from the Interview Service .env file"
    )

# Connect to MongoDB Atlas
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
)

db = client.get_default_database()


def connect_to_mongodb():
    client.admin.command("ping")
    print("MongoDB Atlas connected successfully")


def close_mongodb_connection():
    client.close()
    print("MongoDB connection closed")