from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import shutil
import os

from app.database import database, models

router = APIRouter()

# Define base directories
UPLOADS_DIR = "/home/kenil-kavar/Videos/Tauking Researcher/voice_eda_system/app/data/uploads"
RESULTS_DIR = "/home/kenil-kavar/Videos/Tauking Researcher/voice_eda_system/app/data/results"
AUDIO_DIR = "/home/kenil-kavar/Videos/Tauking Researcher/voice_eda_system/app/data/audio"

@router.delete("/delete/{session_id}")
async def delete_session_data(session_id: str, db: Session = Depends(database.get_db)):
    # Find the session in the database
    session_to_delete = db.query(models.Session).filter(models.Session.session_id == session_id).first()

    if not session_to_delete:
        raise HTTPException(status_code=404, detail="No data found for the given session ID.")

    # Delete associated files and directories
    session_upload_path = os.path.join(UPLOADS_DIR, session_id)
    session_results_path = os.path.join(RESULTS_DIR, session_id)
    session_audio_path = os.path.join(AUDIO_DIR, session_id)

    paths_to_delete = [
        session_upload_path,
        session_results_path,
        session_audio_path
    ]

    deleted_paths = []
    errors = []

    for path in paths_to_delete:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                deleted_paths.append(path)
            except OSError as e:
                errors.append(f"Error deleting {path}: {e.strerror}")

    if errors:
        raise HTTPException(status_code=500, detail=", ".join(errors))

    # Delete database records
    db.query(models.File).filter(models.File.session_id == session_id).delete()
    db.query(models.Log).filter(models.Log.session_id == session_id).delete()
    db.query(models.Session).filter(models.Session.session_id == session_id).delete()
    db.commit()

    return {"message": f"Successfully deleted data for session {session_id}", "deleted_paths": deleted_paths}
