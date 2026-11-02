from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "tracegate.db"
UPLOAD_DIR = DATA_DIR / "uploads"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_TYPES = {".pdf", ".png", ".jpg", ".jpeg"}
