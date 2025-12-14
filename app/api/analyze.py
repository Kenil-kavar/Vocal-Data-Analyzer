from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pandas as pd
import os
import logging
import traceback

from app.core.agent_service import run_eda_workflow
from app.database import database, models

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class AnalysisRequest(BaseModel):
    session_id: str
    text: str

def process_analysis(session_id: str, text: str, dataset_path: str, data_preview: str):
    """
    Background task to run the EDA workflow and update the database.
    """
    # Create a new database session for the background task
    bg_db = database.SessionLocal()
    try:
        logger.info(f"Starting background analysis for session {session_id}")
        # Run the EDA workflow
        result = run_eda_workflow(session_id, text, dataset_path, data_preview)

        try:
            # Save the chat history to the database
            chat_history = result.get("chat_history", [])
            for message in chat_history:
                # Ensure content is a string before logging
                content = message.get("content", "")
                if not isinstance(content, str):
                    content = str(content)

                new_log = models.Log(
                    session_id=session_id,
                    command=message.get("name", message.get("role", "unknown_agent")),
                    output_summary=content
                )
                bg_db.add(new_log)

            # Update session status
            session = bg_db.query(models.Session).filter(models.Session.session_id == session_id).first()
            if session:
                session.status = "completed"
                bg_db.commit()
            
            logger.info(f"Background analysis for session {session_id} completed successfully.")
            
        except Exception as e:
            logger.error(f"Error saving results to DB for session {session_id}: {e}")
            logger.error(traceback.format_exc())
            if session:
                session.status = "failed"
                bg_db.commit()

    except Exception as e:
        logger.error(f"Background analysis failed for session {session_id}: {e}")
        logger.error(traceback.format_exc())
        # Try to update status to failed
        try:
            session = bg_db.query(models.Session).filter(models.Session.session_id == session_id).first()
            if session:
                session.status = "failed"
                bg_db.commit()
        except:
            pass
    finally:
        bg_db.close()

@router.post("/analyze")
async def analyze_data(request: AnalysisRequest, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    try:
        logger.info(f"Received analyze request for session: {request.session_id}")
        
        # Find the session and the associated file
        session = db.query(models.Session).filter(models.Session.session_id == request.session_id).first()
        if not session:
            logger.error(f"Session not found: {request.session_id}")
            raise HTTPException(status_code=404, detail="Session not found.")

        file_record = db.query(models.File).filter(models.File.session_id == request.session_id).first()
        if not file_record:
            logger.error(f"Dataset not found for session: {request.session_id}")
            raise HTTPException(status_code=404, detail="Dataset not found for this session.")

        dataset_path = file_record.file_path
        file_type = file_record.file_type
        
        logger.info(f"Processing file: {dataset_path} ({file_type})")

        # Read the file content to pass to the agent
        try:
            if file_type == '.csv':
                df = pd.read_csv(dataset_path)
            elif file_type == '.xlsx':
                df = pd.read_excel(dataset_path)
            elif file_type == '.json':
                df = pd.read_json(dataset_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
            
            # Get a preview of the data (first 4 rows only)
            data_preview = df.head(2).to_string()
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to read or process the data file: {str(e)}")

        # Update status to running
        session.status = "running"
        db.commit()

        # Add background task
        background_tasks.add_task(process_analysis, request.session_id, request.text, dataset_path, data_preview)

        # Prepare table_data (first 10 rows as records for UI table) - Immediate response
        table_data = []
        try:
            table_data = df.head(10).to_dict(orient="records")
        except Exception:
            table_data = []

        return {
            "message": "Analysis started in background.",
            "session_id": request.session_id,
            "status": "running",
            "table_data": table_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in analyze_data: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
