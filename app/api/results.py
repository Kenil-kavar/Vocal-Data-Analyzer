from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import os

from app.database import database, models

router = APIRouter()

# Use dynamic path instead of hardcoded
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIRECTORY = os.path.join(BASE_DIR, "data", "results")

@router.get("/results/{session_id}")
async def get_results(session_id: str, db: Session = Depends(database.get_db)):
    """Get all result files for a session, grouped by type."""
    session_results_dir = os.path.join(RESULTS_DIRECTORY, session_id)
    
    # Query database for files
    files = db.query(models.File).filter(models.File.session_id == session_id).all()
    
    if not files and not os.path.isdir(session_results_dir):
        raise HTTPException(status_code=404, detail="Results not found for this session.")
    
    # Group files by type
    results = {
        "cleaned_data": [],
        "visualizations": [],
        "chart_code": [],  # New category for chart generation code
        "reports": [],
        "other": []
    }
    
    for file_record in files:
        file_info = {
            "filename": os.path.basename(file_record.file_path),
            "url": f"/data/results/{session_id}/{os.path.basename(file_record.file_path)}",
            "type": file_record.file_type,
            "created_at": str(file_record.created_at)
        }
        
        # Categorize files
        if file_record.file_type in ["cleaned_csv", "cleaned_excel", "cleaned_json"]:
            results["cleaned_data"].append(file_info)
        elif file_record.file_type == "visualization":
            results["visualizations"].append(file_info)
        elif file_record.file_type == "chart_code":
            results["chart_code"].append(file_info)
        elif file_record.file_type == "report":
            results["reports"].append(file_info)
        else:
            results["other"].append(file_info)
    
    return {
        "session_id": session_id, 
        "results": results,
        "total_files": len(files)
    }
