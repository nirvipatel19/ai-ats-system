# ATS Resume Screening System

Role-based AI-powered ATS with **Student** and **Admin** flows, JWT authentication, SQLite database, and agent-based resume screening.

## User Roles

| Role | Actions |
|------|---------|
| **Student** | Register, login, upload resume (PDF), check status (Passed/Rejected) |
| **Admin** | Register, login, set upload deadline, upload JD (PDF/DOCX), run analysis, view ranked candidates |

## Architecture

- **SQLite** – Stores users, resumes, job descriptions, analysis results
- **JWT** – Authentication for all protected routes
- **Agent-Orchestrator** – Parser → Skill → Matching → Ranking → Shortlisting

## Project Structure

```
internal hr tool/
├── backend/
│   ├── agents/           # Parser, Skill, Matching, Ranking, Shortlisting
│   ├── tests/            # Unit tests (pytest)
│   ├── database.py       # SQLite layer
│   ├── auth.py           # JWT + password hashing
│   ├── main.py           # FastAPI app
│   └── requirements.txt
├── frontend/
└── docs/
```

## API Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `POST /register` | No | Register (email, password, role) |
| `POST /login` | No | Returns JWT token |
| `POST /upload-resume` | Student | Upload PDF |
| `GET /my-resumes` | Student | List user's resumes |
| `GET /status/{filename}` | Student | Check application status |
| `POST /submit-jd` | Admin | Upload JD & run analysis |
| `GET /results` | Admin | Ranked candidates |
| `GET /stats` | Admin | Resume count, analysis status |
| `GET/POST /deadline` | Admin | Set upload deadline |

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend: **http://localhost:8000**  
Database file: `backend/ats.db` (created on first run)

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: **http://localhost:3000**

### 3. First Use

1. **Register** an Admin account (role: Admin).
2. **Register** Student accounts.
3. Students upload resumes; Admin sets deadline (optional), uploads JD, runs analysis.

## Unit Tests

```bash
cd backend
pytest
```

Tests cover: skill extraction, ranking, shortlisting.

## Features

- ✅ JWT authentication + registration + login
- ✅ SQLite database (persistent)
- ✅ Upload deadline (Admin sets; Students blocked after)
- ✅ JD from PDF or DOCX
- ✅ Unit tests (pytest)
- ✅ Clean white theme UI
