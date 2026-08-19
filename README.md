# CIVARA (SIH25031, MOOLKARAN Engine)

CIVARA is an advanced geospatial decision-support platform powered by the MOOLKARAN analytical engine for land and resource management. It integrates high-resolution spatial datasets, real-time telemetry, and modular predictive workflows to enable scalable civic and environmental governance. Built as a high-performance modular monolith, CIVARA seamlessly unites spatial databases, asynchronous job processing, and reactive user interfaces.

## Project Structure

```text
CIVARA/
├── backend/                # FastAPI backend service (Python 3.11+)
│   ├── app/
│   │   ├── api/            # Base API endpoints (e.g., /health)
│   │   ├── core/           # Core configuration & settings
│   │   └── modules/        # Domain modules (models, schemas, service, router)
│   ├── tests/              # Backend test suite (pytest)
│   ├── Dockerfile          # Backend Docker definition
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js 15 frontend application (TypeScript, App Router)
│   ├── app/                # App Router pages and layout
│   ├── package.json        # Node dependencies & scripts
│   └── tsconfig.json       # TypeScript configuration
├── docker-compose.yml      # Infrastructure services (PostgreSQL + PostGIS, Redis)
├── .env.example            # Documented environment variable template
└── README.md               # Project documentation
```

## Quick Start

### 1. Start Infrastructure Services

Ensure Docker Desktop is running, then launch PostgreSQL (PostGIS) and Redis:

```bash
docker compose up -d
```

### 2. Run Backend Locally

Navigate to the `backend/` directory, create a virtual environment, install dependencies, and launch the server:

```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

The backend API will be available at [http://localhost:8005](http://localhost:8005).  
Check health status at [http://localhost:8005/health](http://localhost:8005/health).

### 3. Run Frontend Locally

In a new terminal, navigate to the `frontend/` directory, install dependencies, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3005](http://localhost:3005) in your browser. The home page will check the backend health endpoint and display **"Backend connected"**.

## Testing

Run backend tests using `pytest`:

```bash
cd backend
pytest
```
