
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFSBucket


# Load User Service environment variables
SERVICE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(SERVICE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is missing from the User Service .env file"
    )

# Create MongoDB client
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
)

# Get the default database
db = client.get_default_database()

# Initialize GridFS for profile images
profile_images_bucket = GridFSBucket(
    db,
    bucket_name="profile_images",
)


def connect_to_mongodb():
    """Verify the MongoDB connection."""
    client.admin.command("ping")
    print("MongoDB Atlas connected successfully")


def close_mongodb_connection():
    """Close the MongoDB client."""
    client.close()
