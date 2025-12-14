# Voice-Based Exploratory Data Analysis System

A powerful AI-driven voice-based system for performing exploratory data analysis (EDA) on your datasets. Upload your data, speak your analysis requests, and get visualizations, cleaned data, and insights automatically.

## Features

- 🎤 **Voice Input**: Use voice commands to analyze your data
- 📊 **Automated EDA**: AI agents automatically clean data and generate visualizations
- 📈 **Multiple Chart Types**: Histograms, bar charts, pie charts, scatter plots, and more
- 💾 **Download Results**: Get all generated files (cleaned data, graphs, reports) as a ZIP
- 🔄 **Real-time Status**: Track analysis progress with live status updates
- 🗄️ **Database Storage**: All results are stored and linked to session IDs

## Tech Stack

- **Backend**: FastAPI, Python 3.11, SQLAlchemy
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **AI**: Autogen (Microsoft), Groq API (LLaMA models)
- **Deployment**: Docker, Docker Compose

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm (for local development)
- Groq API Keys (get from [console.groq.com](https://console.groq.com))

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Kenil-kavar/Vocal-Data-Analyzer.git
cd Vocal-Data-Analyzer
```

### 2. Create Environment File

Create a `.env` file in the project root directory:

```bash
touch .env
```

Add the following content to `.env`:

```env
# Groq API Keys (Get from https://console.groq.com)
# You need 4 separate API keys for parallel agent processing
GROQ_API_KEY1=your_groq_api_key_here
GROQ_API_KEY2=your_groq_api_key_here
GROQ_API_KEY3=your_groq_api_key_here
GROQ_API_KEY4=your_groq_api_key_here

# Database Configuration
DATABASE_URL="sqlite:///./database/eda_database.db"
```

**Important Notes**:
- Replace `your_groq_api_key_here` with your actual Groq API keys
- You can use the same API key for all 4 entries, but having separate keys prevents rate limiting
- The database will be automatically created in the `database/` folder
- **Never commit the `.env` file to version control** (already in `.gitignore`)

### 3. Build and Start the Application

```bash
# Build and start all services (backend + frontend)
sudo docker compose up --build
```

**First-time setup may take a few minutes** to:
- Pull Docker images
- Install Python dependencies
- Install Node.js dependencies
- Build the React frontend

### 4. Access the Application

Once Docker is running, open your browser:

```
http://localhost:8080
```

## Usage Guide

### Step 1: Upload Data

1. Click the **file upload** area or drag & drop your file
2. Supported formats: **CSV**, **Excel (.xlsx)**, **JSON**
3. Wait for upload confirmation

### Step 2: Analyze Your Data

**Option A: Voice Input** 🎤
1. Click the microphone button
2. Speak your request (e.g., "Clean the data and create visualizations")
3. Click stop when done

**Option B: Text Input** ⌨️
1. Type your request in the input box
2. Press Enter or click Send

**Example Prompts**:
- "Clean the data and remove missing values"
- "Create a histogram for patient ages"
- "Generate pie charts showing department distribution"
- "Analyze the data and create all relevant visualizations"

### Step 3: Wait for Processing

- You'll see a "🔄 Processing..." message
- The system polls the backend every 2 seconds for status
- Processing time varies (10s - 2 minutes depending on data size and complexity)

### Step 4: Download Results

- When complete, you'll see: "✅ Analysis complete!"
- Click **"Download All Results"** button to get a ZIP file containing:
  - Cleaned data files (CSV/Excel/JSON)
  - Generated visualizations (PNG images)
  - Summary reports (Excel)
  - Graph data (JSON)

### Step 5: Delete Session (Optional)

- Click **"Delete Data"** to remove session files and clear the database

## Development

### Running Frontend Locally (without Docker)

```bash
cd app/frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:8080`

### Running Backend Locally (without Docker)

```bash
cd app
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at `http://localhost:8000`

## Project Structure

```
voice_eda_system/
├── app/
│   ├── agents/          # Autogen agent configurations
│   ├── api/             # FastAPI endpoints
│   ├── core/            # Core services (agent workflow)
│   ├── database/        # SQLAlchemy models and DB config
│   ├── data/
│   │   ├── uploads/     # Uploaded files (by session_id)
│   │   └── results/     # Generated results (by session_id)
│   ├── frontend/        # React + Vite frontend
│   └── main.py          # FastAPI application entry point
├── coding/              # Temporary code execution directory
├── .env                 # Environment variables (CREATE THIS!)
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Backend container definition
├── requirements.txt     # Python dependencies
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload data file |
| `/analyze` | POST | Start analysis (background task) |
| `/status/{session_id}` | GET | Check analysis status |
| `/download/{session_id}` | GET | Download results as ZIP |
| `/delete/{session_id}` | DELETE | Delete session data |
| `/voice` | POST | Transcribe voice to text |
| `/results/{session_id}` | GET | Get result file metadata |

## Troubleshooting

### "Analysis Failed" Error

**Cause**: The `/status` endpoint might not be available in the running container.

**Solution**: Rebuild Docker containers to load the latest code:
```bash
sudo docker compose down
sudo docker compose up --build
```

### Groq API Rate Limits

**Cause**: Using same API key for all agents or hitting rate limits.

**Solution**: 
- Get multiple Groq API keys
- Add them to `.env` file (GROQ_API_KEY1 through GROQ_API_KEY4)
- Restart Docker

### Port Already in Use

**Cause**: Port 8080 or 8000 is already occupied.

**Solution**:
```bash
# Find and kill the process using the port
sudo lsof -ti:8080 | xargs kill -9
sudo lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

### Frontend Not Loading

**Cause**: Frontend build failed or proxy misconfigured.

**Solution**:
1. Check `app/frontend/vite.config.js` has correct proxy settings
2. Rebuild: `sudo docker compose up --build`
3. Check browser console for errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: [Your Email/Contact Info]

## Acknowledgments

- Built with [Autogen](https://github.com/microsoft/autogen) by Microsoft
- Powered by [Groq](https://groq.com/) AI inference
- UI components from [shadcn/ui](https://ui.shadcn.com/)
