from database import get_conn
import sqlite3
from agents.parser_agent import parse_document_text

def fill_missing_jd_text():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, filename, content FROM job_descriptions WHERE description_text IS NULL OR description_text = ''")
    rows = cur.fetchall()
    
    print(f"Found {len(rows)} JDs missing text. Processing...")
    
    for row in rows:
        jd_id = row[0]
        filename = row[1]
        content = row[2]
        print(f"Processing JD ID {jd_id}: {filename}")
        
        text, ok = parse_document_text(content, filename)
        
        if ok:
            cur.execute("UPDATE job_descriptions SET description_text = ? WHERE id = ?", (text, jd_id))
            print(f"  Successfully updated text ({len(text)} chars)")
        else:
            print(f"  Failed to extract text for {filename}")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    fill_missing_jd_text()
