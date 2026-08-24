from fastapi import APIRouter, Depends, status
from app.database.connection import get_db
from pymongo.database import Database
import time

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/liveness", status_code=status.HTTP_200_OK)
def check_liveness():
    """Simple endpoint to verify the API is running."""
    return {"status": "ok", "timestamp": time.time()}

@router.get("/readiness", status_code=status.HTTP_200_OK)
def check_readiness(db: Database = Depends(get_db)):
    """Check if upstream dependencies (e.g., MongoDB) are reachable."""
    try:
        # Ping the database
        db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database connection failed: {str(e)}")
