from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import requests

router = APIRouter()

# Define the base directory for audio files
AUDIO_DIRECTORY = "/home/kenil-kavar/Videos/Tauking Researcher/voice_eda_system/app/data/audio"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

@router.post("/voice")
async def handle_voice(session_id: str = Form(...), file: UploadFile = File(...)):
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required.")

    session_audio_dir = os.path.join(AUDIO_DIRECTORY, session_id)
    os.makedirs(session_audio_dir, exist_ok=True)

    # Save the audio file
    file_path = os.path.join(session_audio_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Send to Groq API for transcription
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API key is not configured.")

    try:
        with open(file_path, "rb") as audio_file:
            files = {
                'file': (file.filename, audio_file, file.content_type),
                'model': (None, 'whisper-large-v3'),
            }
            headers = {'Authorization': f'Bearer {GROQ_API_KEY}'}
            response = requests.post(GROQ_API_URL, files=files, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            transcribed_text = response.json().get("text", "")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {e}")
    finally:
        # Clean up the temporary audio file
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"session_id": session_id, "transcribed_text": transcribed_text}
