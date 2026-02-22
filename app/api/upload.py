from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import shutil
import os
import uuid

from app.database import database, models

router = APIRouter()

# Define the base directory for uploads using dynamic path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIRECTORY = os.path.join(BASE_DIR, "data", "uploads")

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    session_upload_dir = os.path.join(UPLOAD_DIRECTORY, session_id)
    os.makedirs(session_upload_dir, exist_ok=True)

    # Validate file type
    allowed_extensions = {".csv", ".xlsx", ".json"}
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types are {', '.join(allowed_extensions)}")

    # Save the uploaded file
    file_path = os.path.join(session_upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create a new session in the database
    new_session = models.Session(session_id=session_id, dataset_name=file.filename)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Add file record to the database
    new_file = models.File(
        session_id=session_id,
        file_type=file_extension,
        file_path=file_path
    )
    db.add(new_file)
    db.commit()

    return {"session_id": session_id, "filename": file.filename, "path": file_path}
