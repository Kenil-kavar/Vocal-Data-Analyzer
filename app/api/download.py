from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from app.database import database, models
import os
import shutil
import tempfile
from fastapi.responses import FileResponse

router = APIRouter()

# Use dynamic paths like results.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIRECTORY = os.path.join(BASE_DIR, "data", "results")
UPLOADS_DIRECTORY = os.path.join(BASE_DIR, "data", "uploads")

@router.get("/download/{session_id}")
def download_session_files(session_id: str, db: Session = Depends(database.get_db)):
    # Get all files from results and uploads for this session
    files = []
    session_results_dir = os.path.join(RESULTS_DIRECTORY, session_id)
    session_uploads_dir = os.path.join(UPLOADS_DIRECTORY, session_id)
    for d in [session_results_dir, session_uploads_dir]:
        if os.path.isdir(d):
            for f in os.listdir(d):
                fpath = os.path.join(d, f)
                if os.path.isfile(fpath):
                    files.append((f, fpath))
    if not files:
        raise HTTPException(status_code=404, detail="No files found for this session.")
    # Create a zip file in a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        from zipfile import ZipFile
        with ZipFile(tmp, 'w') as zipf:
            for fname, fpath in files:
                zipf.write(fpath, arcname=fname)
        tmp_path = tmp.name
    return FileResponse(tmp_path, filename=f"session_{session_id}_files.zip", media_type="application/zip")
