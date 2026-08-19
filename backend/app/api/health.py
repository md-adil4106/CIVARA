from fastapi import APIRouter
from sqlalchemy import create_engine, text
from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    db_ok = False
    try:
        # Create a short-lived connection to verify database availability
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"connect_timeout": 3}
        )
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                db_ok = True
        engine.dispose()
    except Exception:
        db_ok = False

    return {"status": "ok", "db": db_ok}
