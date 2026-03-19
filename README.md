# Premium Academic AI-powered ATS System

A modern, high-performance Applicant Tracking System (ATS) built with **FastAPI**, **React**, and **Agent-based AI**. This system has been specifically tailored for academic use cases, allowing professors and administrators to bulk-upload folders of student resumes or ZIP files and automatically rank them against specific Job Descriptions (JDs) or Rubrics.

---

## 🌟 Key Features

### 🚀 Performance & Scale
- **Parallel Processing**: Uses multi-threading (ThreadPoolExecutor) to analyze multiple resumes simultaneously.
- **Lazy Loading**: Heavy AI models and OCR libraries are loaded on-demand, ensuring instant backend startup.

### 🧠 Intelligent AI Agents
- **Fuzzy Skill Matching**: Implements a normalization engine that treats `React`, `ReactJS`, and `React.js` as the same skill, significantly improving match accuracy.
- **Strict Tech Extraction**: Optimized to ignore noise (months, locations, soft skills) and focus exclusively on programming languages, frameworks, and tools.
- **Advanced OCR (300 DPI)**: High-resolution scanning ensures reliable text extraction from scanned or image-based PDF resumes.

### 🎨 User Experience
- **Academic Admin Console**: A single-view centralized dashboard to manage pipelines, upload bulk student data (folders or ZIPs), and view real-time analysis.
- **Glassmorphism UI**: A premium, modern design with real-time feedback and smooth animations.

---

## 📋 System Assumptions

The system has been designed with the following core business logic and assumptions:

1. **Technical Primacy**: The screening logic prioritizes technical tech-stack overlap. Soft skills (e.g., "Leadership") and education levels (e.g., "B.Tech") are excluded from the primary skill-matching score to ensure objective technical vetting.
2. **60% Shortlist Bar**: A candidate is automatically marked as **"Shortlisted"** if they possess at least **60%** of the technical skills extracted from the Job Description.
3. **Academic Workflow**: The system is designed for professors/admins to upload folders or `.zip` files of multiple student resumes against a specific rubric or JD, evaluating entire cohorts simultaneously.
4. **Semantic Match Fallback**: While skill-matching is the primary shortlisting criteria, the system calculates a secondary **Semantic AI Score** (using Sentence-Transformers) to understand the broader context and descriptive experience in a resume.

---

## 🛠️ Technology Stack

-   **Backend**: FastAPI, Python, SQLite (Aiosqlite)
-   **Frontend**: React.js, Vite, Vanilla CSS (Premium Glassmorphism)
-   **AI Helpers**: 
    -   `SentenceTransformers` (Semantic matching)
    -   `Pytesseract` (OCR Scanning)
    -   `pdfplumber` (PDF Parsing)
-   **Security**: JWT (JSON Web Tokens), BCrypt Password Hashing

---

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
*Backend runs on `http://localhost:8000`*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000`*

---

## 📂 Project Structure

```text
├── backend/
│   ├── agents/           # Parser, Skill, Matching, Ranking, Shortlisting Agents
│   ├── database.py       # SQLite Layer & ORM-like functions
│   ├── auth.py           # Security & JWT logic
│   ├── orchestrator.py    # Pipeline coordinator (Parallelized)
│   └── main.py           # API endpoints
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main Dashboard Logic
│   │   └── App.css       # Premium Styling
└── .gitignore            # Protects DB and private files
```

---

## 🤝 Contributing
1. Initialize Git: `git init`
2. Add remote: `git remote add origin <repo_url>`
3. Push changes: `git push -u origin main`

---
**Developed by Nirvi & Powered by AI Agents 🚀**
