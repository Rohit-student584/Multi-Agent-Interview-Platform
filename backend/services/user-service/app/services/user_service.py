from datetime import datetime, timezone
from io import BytesIO

from bson import ObjectId
from gridfs.errors import NoFile

from app.core.database import db, profile_images_bucket


# MongoDB users collection
users_collection = db["users"]


def serialize_user(user: dict) -> dict:
    """Convert a MongoDB user document into API-friendly data."""
    return {
        "id": str(user["_id"]),
        "firebase_uid": user["firebase_uid"],
        "email": user["email"],
        "name": user["name"],
        "target_role": user.get("target_role"),
        "skills": user.get("skills", []),
    }


def create_or_update_user_profile(
    firebase_uid: str,
    email: str,
    profile_data: dict,
) -> dict:
    """Create a user profile or update the existing profile."""

    now = datetime.now(timezone.utc)

    users_collection.update_one(
        {"firebase_uid": firebase_uid},
        {
            "$set": {
                "email": email,
                "name": profile_data["name"],
                "target_role": profile_data.get("target_role"),
                "skills": profile_data.get("skills", []),
                "updated_at": now,
            },
            "$setOnInsert": {
                "firebase_uid": firebase_uid,
                "created_at": now,
            },
        },
        upsert=True,
    )

    user = users_collection.find_one({"firebase_uid": firebase_uid})

    if user is None:
        raise RuntimeError("Failed to retrieve the saved user profile")

    return serialize_user(user)


def get_user_profile(firebase_uid: str) -> dict | None:
    """Retrieve a user profile using the Firebase UID."""

    user = users_collection.find_one({"firebase_uid": firebase_uid})

    if user is None:
        return None

    return serialize_user(user)


def save_profile_image(
    firebase_uid: str,
    image_content: bytes,
    filename: str,
    content_type: str,
) -> dict:
    """Upload or replace a user's profile image in MongoDB GridFS."""

    user = users_collection.find_one({
        "firebase_uid": firebase_uid
    })

    if user is None:
        raise LookupError("User profile not found.")

    if not image_content:
        raise ValueError("Profile image cannot be empty.")

    old_image_id = user.get("profile_image_id")

    # Upload new image to GridFS
    new_image_id = profile_images_bucket.upload_from_stream(
        filename,
        BytesIO(image_content),
        metadata={
            "firebase_uid": firebase_uid,
            "content_type": content_type,
        },
    )

    now = datetime.now(timezone.utc)

    result = users_collection.update_one(
        {"firebase_uid": firebase_uid},
        {
            "$set": {
                "profile_image_id": new_image_id,
                "updated_at": now,
            }
        },
    )

    if result.matched_count != 1:
        profile_images_bucket.delete(new_image_id)
        raise RuntimeError("Failed to update user profile image.")

    # Delete previous image after successful replacement
    if old_image_id and old_image_id != new_image_id:
        try:
            profile_images_bucket.delete(old_image_id)
        except NoFile:
            pass

    return {
        "profile_image_id": str(new_image_id),
        "filename": filename,
        "message": "Profile image uploaded successfully.",
    }


def get_profile_image(firebase_uid: str) -> dict | None:
    """Retrieve a user's profile image from GridFS."""

    user = users_collection.find_one({
        "firebase_uid": firebase_uid
    })

    if user is None:
        raise LookupError("User profile not found.")

    image_id = user.get("profile_image_id")

    if not image_id:
        return None

    try:
        image_stream = profile_images_bucket.open_download_stream(
            image_id
        )
    except NoFile:
        return None

    metadata = image_stream.metadata or {}

    return {
        "content": image_stream.read(),
        "content_type": metadata.get(
            "content_type",
            "application/octet-stream",
        ),
        "filename": image_stream.filename,
    }


def delete_profile_image(firebase_uid: str) -> dict:
    """Delete a user's profile image from GridFS."""

    user = users_collection.find_one({
        "firebase_uid": firebase_uid
    })

    if user is None:
        raise LookupError("User profile not found.")

    image_id = user.get("profile_image_id")

    if not image_id:
        raise LookupError("Profile image not found.")

    try:
        profile_images_bucket.delete(image_id)
    except NoFile:
        pass

    users_collection.update_one(
        {"firebase_uid": firebase_uid},
        {
            "$unset": {
                "profile_image_id": "",
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc),
            },
        },
    )

    return {
        "message": "Profile image deleted successfully."
    }
