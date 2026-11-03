from io import BytesIO
from pathlib import Path
import zipfile

import fitz
from docx import Document
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import get_current_user
from app.services.resume_service import (
    create_resume_record,
    get_user_resumes,
)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Validate, extract text, and save resume data."""

    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX resumes are supported.",
        )

    file_bytes = await file.read(MAX_FILE_SIZE + 1)
    await file.close()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume size must not exceed 5 MB.",
        )

    try:
        if extension == ".pdf":
            if not file_bytes.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail="The uploaded file is not a valid PDF.",
                )

            with fitz.open(
                stream=file_bytes,
                filetype="pdf",
            ) as document:
                if document.is_encrypted:
                    raise HTTPException(
                        status_code=400,
                        detail="Password-protected PDFs are not supported.",
                    )

                extracted_text = "\n".join(
                    page.get_text() for page in document
                )

        else:
            with zipfile.ZipFile(BytesIO(file_bytes)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise HTTPException(
                        status_code=400,
                        detail="The uploaded file is not a valid DOCX.",
                    )

            document = Document(BytesIO(file_bytes))
            extracted_text = "\n".join(
                paragraph.text for paragraph in document.paragraphs
            )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="The resume file is corrupted or cannot be read.",
        ) from exc

    extracted_text = extracted_text.strip()

    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the resume.",
        )

    try:
        saved_resume = create_resume_record(
            firebase_uid=firebase_uid,
            filename=Path(filename).name,
            file_type=extension[1:],
            extracted_text=extracted_text,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to save resume data.",
        ) from exc

    return {
        "success": True,
        "message": "Resume uploaded, text extracted, and data saved successfully.",
        "resume_id": saved_resume["id"],
        "filename": saved_resume["filename"],
        "file_type": saved_resume["file_type"],
        "extracted_characters": saved_resume["extracted_characters"],
        "text_preview": extracted_text[:300],
    }

@router.get("/my")
def list_my_resumes(
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    resumes = get_user_resumes(firebase_uid)

    return {
        "success": True,
        "count": len(resumes),
        "resumes": resumes,
    }