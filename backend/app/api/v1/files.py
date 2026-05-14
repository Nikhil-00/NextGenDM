import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.schemas.files import FileResponse
from app.services.storage_service import upload_file, delete_file, ensure_bucket_exists

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=FileResponse, status_code=201)
async def upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: PDF, JPEG, PNG, GIF",
        )
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    ensure_bucket_exists()
    file_url, bucket_path = upload_file(contents, file.filename, file.content_type, str(current_user.id))

    db_file = UploadedFile(
        user_id=current_user.id,
        filename=f"{uuid.uuid4()}_{file.filename}",
        original_filename=file.filename,
        file_url=file_url,
        file_size=len(contents),
        mime_type=file.content_type,
        bucket_path=bucket_path,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.get("/", response_model=list[FileResponse])
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.created_at.desc())
        .all()
    )


@router.delete("/{file_id}")
def delete(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id,
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    if db_file.bucket_path:
        delete_file(db_file.bucket_path)
    db.delete(db_file)
    db.commit()
    return {"message": "File deleted"}
