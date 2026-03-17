"""FastAPI ATS Resume Screening Backend - Role-based API with Auth & DB."""
import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from agents.parser_agent import parse_document_text
from auth import create_token, decode_token, hash_password, verify_password
from database import (
    add_job_description,
    add_resume,
    create_user,
    get_admin_count,
    get_all_jds,
    get_jd_by_id,
    get_latest_analysis_result,
    get_resume_by_user_and_jd,
    get_resume_count_for_jd,
    get_resume_filenames_by_user,
    get_resumes_for_jd,
    get_upload_deadline,
    get_user_by_email,
    get_user_by_id,
    init_db,
    save_analysis_result,
    set_upload_deadline,
)
from orchestrator import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATS Resume Screening API",
    description="Role-based ATS with Student upload & Admin analysis",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(creds.credentials)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return dict(user)


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ---- Models ----

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SetDeadlineRequest(BaseModel):
    deadline: Optional[str] = None  # ISO format or null to clear


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized")


@app.get("/")
def root():
    return {"message": "ATS API", "docs": "/docs"}


# ---- Auth (public) ----

@app.post("/register")
def register(req: RegisterRequest):
    """Student or Admin registration."""
    if get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")
        
    admin_count = get_admin_count()
    role = "admin" if admin_count == 0 else "student"
    
    pw_hash = hash_password(req.password)
    create_user(req.email.lower(), pw_hash, role)
    return {"message": "Registered successfully", "role": role}


@app.post("/login")
def login(req: LoginRequest):
    """Returns JWT token."""
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"user_id": user["id"], "role": user["role"]})
    return {"access_token": token, "role": user["role"]}


# ---- Student endpoints (auth required) ----

@app.post("/upload-resume")
async def upload_resume(
    jd_id: int,
    resume: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Students only")
    
    jd = get_jd_by_id(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    deadline = get_upload_deadline()
    if deadline and datetime.utcnow() > deadline:
        raise HTTPException(status_code=400, detail="Upload deadline has passed.")
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # NEW: Check for duplicate application
    existing = get_resume_by_user_and_jd(user["id"], jd_id)
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this role.")
    
    content = await resume.read()
    add_resume(user["id"], jd_id, resume.filename, content)
    logger.info(f"Stored resume: {resume.filename} for user {user['id']} JD {jd_id}")
    return {
        "message": "Resume uploaded successfully",
        "filename": resume.filename,
        "total_resumes": get_resume_count_for_jd(jd_id),
    }


@app.get("/jds")
def list_jds():
    """List all available job descriptions."""
    return {"jds": get_all_jds()}


@app.get("/my-resumes")
def my_resumes(user: dict = Depends(get_current_user)):
    """List filenames of current user's resumes."""
    names = get_resume_filenames_by_user(user["id"])
    return {"resumes": names}


@app.get("/status/{jd_id}/{filename}")
def get_status(
    jd_id: int,
    filename: str,
    user: dict = Depends(get_current_user),
):
    result = get_latest_analysis_result(jd_id)
    if not result or "candidates" not in result:
        return {
            "filename": filename,
            "status": "pending",
            "passed": None,
            "message": "No analysis run yet. Admin will process applications soon.",
        }
    for c in result["candidates"]:
        if c.get("filename") == filename:
            passed = c.get("status") == "Shortlisted"
            return {
                "filename": filename,
                "name": c.get("name"),
                "score": c.get("score"),
                "status": c.get("status"),
                "passed": passed,
                "message": "Accepted." if passed else "Rejected",
                "rank": next(
                    (i + 1 for i, x in enumerate(result["candidates"]) if x.get("filename") == filename),
                    None,
                ),
            }
    return {
        "filename": filename,
        "status": "not_found",
        "passed": None,
        "message": "Resume not found. Ensure you uploaded before the deadline.",
    }


# ---- Admin endpoints (admin auth required) ----

@app.post("/submit-jd")
async def submit_jd(
    title: str = Form(...),
    jd_document: UploadFile = File(...),
    admin: dict = Depends(require_admin),
):
    fn = (jd_document.filename or "").lower()
    if not fn or (not fn.endswith(".pdf") and not fn.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Job description must be PDF or DOCX.")
    
    content = await jd_document.read()
    
    # Extract text from JD so students can read it in the portal
    jd_text, _ = parse_document_text(content, jd_document.filename)
    
    jd_id = add_job_description(title, jd_document.filename, content, description_text=jd_text)
    logger.info(f"Stored JD: {title} (ID: {jd_id})")
    return {"message": "Job description submitted successfully", "jd_id": jd_id}


@app.post("/run-analysis/{jd_id}")
async def run_analysis(
    jd_id: int,
    admin: dict = Depends(require_admin),
):
    jd = get_jd_by_id(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    resume_files = get_resumes_for_jd(jd_id)
    if not resume_files:
        raise HTTPException(status_code=400, detail="No resumes uploaded for this JD yet.")

    jd_text, ok = parse_document_text(jd["content"], jd["filename"])
    if not ok or not jd_text.strip():
        raise HTTPException(status_code=500, detail="Could not extract text from JD document.")

    try:
        result = run_pipeline(jd_text, resume_files)
        save_analysis_result(jd_id, result)
        return result
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{jd_id}")
def get_results(
    jd_id: int,
    admin: dict = Depends(require_admin)
):
    result = get_latest_analysis_result(jd_id)
    if not result:
        return {"candidates": [], "logs": [], "message": "No analysis run yet for this JD."}
    return result


@app.get("/stats/{jd_id}")
def get_stats(
    jd_id: int,
    admin: dict = Depends(require_admin)
):
    return {
        "resume_count": get_resume_count_for_jd(jd_id),
        "has_analysis": get_latest_analysis_result(jd_id) is not None,
    }


@app.get("/deadline")
def get_deadline(admin: dict = Depends(require_admin)):
    d = get_upload_deadline()
    return {"deadline": d.isoformat() if d else None}


@app.post("/deadline")
def set_deadline(req: SetDeadlineRequest, admin: dict = Depends(require_admin)):
    if req.deadline:
        try:
            dt = datetime.fromisoformat(req.deadline.replace("Z", "+00:00"))
            set_upload_deadline(dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO 8601.")
    else:
        set_upload_deadline(None)
    return {"deadline": req.deadline}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
