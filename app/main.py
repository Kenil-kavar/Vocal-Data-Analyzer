from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, voice, analyze, results, delete, download, status
from app.database import database, models

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Voice-Based Exploratory Data Analysis System",
    description="An AI-driven voice-based system for EDA.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:3000", # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(voice.router, tags=["Voice"])
app.include_router(analyze.router, tags=["Analyze"])
app.include_router(results.router, tags=["Results"])
app.include_router(delete.router, tags=["Delete"])
app.include_router(download.router, tags=["Download"])
app.include_router(status.router, tags=["Status"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Voice-Based Exploratory Data Analysis System!"}
