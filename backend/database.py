"""SQLite database layer for ATS."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "ats.db"


def get_conn():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            jd_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            content BLOB NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
        );

        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            content BLOB NOT NULL,
            description_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_id INTEGER NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        INSERT OR IGNORE INTO settings (key, value) VALUES ('upload_deadline', NULL);
    """)
    conn.commit()
    conn.close()


def get_setting(key: str) -> str | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(key: str, value: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def get_upload_deadline() -> datetime | None:
    val = get_setting("upload_deadline")
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        return None


def set_upload_deadline(dt: datetime | None):
    set_setting("upload_deadline", dt.isoformat() if dt else "")
    # Also handle empty string for clearing


def get_admin_count() -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM users WHERE role = 'admin'")
    row = cur.fetchone()
    conn.close()
    return row["c"] if row else 0


def create_user(email: str, password_hash: str, role: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
        (email, password_hash, role),
    )
    uid = cur.lastrowid
    conn.commit()
    conn.close()
    return uid


def get_user_by_email(email: str) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def add_resume(user_id: int, jd_id: int, filename: str, content: bytes):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resumes (user_id, jd_id, filename, content) VALUES (?, ?, ?, ?)",
        (user_id, jd_id, filename, content),
    )
    conn.commit()
    conn.close()


def get_resume_by_user_and_jd(user_id: int, jd_id: int) -> dict | None:
    """Check if a user has already uploaded a resume for this JD."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM resumes WHERE user_id = ? AND jd_id = ?", (user_id, jd_id))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_resumes_for_jd(jd_id: int) -> list[tuple[str, bytes]]:
    """Return list of (filename, content) for all resumes uploaded for a specific JD."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT filename, content FROM resumes WHERE jd_id = ? ORDER BY created_at", (jd_id,))
    rows = cur.fetchall()
    conn.close()
    return [(r["filename"], bytes(r["content"])) for r in rows]


def add_job_description(title: str, filename: str, content: bytes, description_text: str = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO job_descriptions (title, filename, content, description_text) VALUES (?, ?, ?, ?)",
        (title, filename, content, description_text),
    )
    jd_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jd_id


def get_all_jds() -> list[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, filename, description_text, created_at FROM job_descriptions ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_jd_by_id(jd_id: int) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_descriptions WHERE id = ?", (jd_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_analysis_result(jd_id: int, result: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analysis_results (jd_id, result_json) VALUES (?, ?)",
        (jd_id, json.dumps(result)),
    )
    conn.commit()
    conn.close()


def get_latest_analysis_result(jd_id: int) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT result_json FROM analysis_results WHERE jd_id = ? ORDER BY id DESC LIMIT 1",
        (jd_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row["result_json"])


def get_resume_filenames_by_user(user_id: int) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.filename, j.title as jd_title 
        FROM resumes r 
        JOIN job_descriptions j ON r.jd_id = j.id 
        WHERE r.user_id = ? 
        ORDER BY r.created_at DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_resume_count_for_jd(jd_id: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM resumes WHERE jd_id = ?", (jd_id,))
    n = cur.fetchone()["c"]
    conn.close()
    return n
