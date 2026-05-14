import uuid
from app.core.config import settings

BUCKET_NAME = "nextgendm-files"

_supabase_client = None


def _get_client():
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client


def ensure_bucket_exists() -> None:
    try:
        _get_client().storage.create_bucket(BUCKET_NAME, options={"public": True})
    except Exception:
        pass


def upload_file(file_bytes: bytes, filename: str, content_type: str, user_id: str) -> tuple[str, str]:
    path = f"{user_id}/{uuid.uuid4()}_{filename}"
    _get_client().storage.from_(BUCKET_NAME).upload(
        path,
        file_bytes,
        file_options={"content-type": content_type},
    )
    public_url = _get_client().storage.from_(BUCKET_NAME).get_public_url(path)
    return public_url, path


def delete_file(bucket_path: str) -> None:
    _get_client().storage.from_(BUCKET_NAME).remove([bucket_path])
