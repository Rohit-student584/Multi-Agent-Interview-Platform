from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Response,
)

from app.api.dependencies import get_current_user
from app.schemas.user import UserProfileCreate, UserProfileResponse
from app.services.user_service import (
    create_or_update_user_profile,
    get_user_profile,
    save_profile_image,
    get_profile_image,
    delete_profile_image,
)


router = APIRouter(tags=["Users"])


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    profile_data: UserProfileCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create or update the authenticated user's profile."""

    firebase_uid = current_user.get("uid")
    email = current_user.get("email")

    if not firebase_uid or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid authenticated user with an email is required.",
        )

    return create_or_update_user_profile(
        firebase_uid=firebase_uid,
        email=email,
        profile_data=profile_data.model_dump(),
    )


@router.get("/me", response_model=UserProfileResponse)
def read_my_profile(
    current_user: dict = Depends(get_current_user),
):
    """Retrieve the authenticated user's profile."""

    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity.",
        )

    profile = get_user_profile(firebase_uid)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Create your profile first.",
        )

    return profile


@router.post("/me/profile-image")
async def upload_my_profile_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    allowed_types = {
        "image/jpeg": [".jpg", ".jpeg"],
        "image/png": [".png"],
        "image/webp": [".webp"],
    }

    filename = (file.filename or "").lower()
    content_type = file.content_type

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are supported.",
        )

    if not any(filename.endswith(ext) for ext in allowed_types[content_type]):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file extension.",
        )

    image_content = await file.read()

    if not image_content:
        raise HTTPException(
            status_code=400,
            detail="Please select an image.",
        )

    if len(image_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Profile image must not exceed 5 MB.",
        )

    # Verify actual image format using file signature
    valid_signatures = {
        "image/jpeg": image_content.startswith(b"\xff\xd8\xff"),
        "image/png": image_content.startswith(
            b"\x89PNG\r\n\x1a\n"
        ),
        "image/webp": (
            len(image_content) >= 12
            and image_content.startswith(b"RIFF")
            and image_content[8:12] == b"WEBP"
        ),
    }

    if not valid_signatures[content_type]:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    try:
        result = save_profile_image(
            firebase_uid=firebase_uid,
            image_content=image_content,
            filename=file.filename,
            content_type=content_type,
        )

        return {
            "success": True,
            "message": "Profile image uploaded successfully.",
            "data": result,
        }

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/me/profile-image")
def read_my_profile_image(
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        image = get_profile_image(firebase_uid)

        if image is None:
            raise HTTPException(
                status_code=404,
                detail="Profile image not found.",
            )

        return Response(
            content=image["content"],
            media_type=image["content_type"],
            headers={"Cache-Control": "private, no-store"},
        )

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/me/profile-image")
def remove_my_profile_image(
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = delete_profile_image(firebase_uid)

        return {
            "success": True,
            "message": result["message"],
        }

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
