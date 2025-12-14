from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import database, models

router = APIRouter()

@router.get("/status/{session_id}")
async def get_session_status(session_id: str, db: Session = Depends(database.get_db)):
    """Get the current status of a session."""
    session = db.query(models.Session).filter(
        models.Session.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": session.status,  # "created", "running", "completed", "failed"
        "created_at": str(session.created_at),
        "dataset_name": session.dataset_name
    }
