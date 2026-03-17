"""Skill Extraction Agent - Extracts keywords/skills from resume text."""
import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# Strict Technical Skill Patterns
SKILL_PATTERNS = [
    # Programming Languages
    r"\b(python|javascript|java|c\+\+|c\#|ruby|golang|rust|swift|kotlin|php|typescript|scala|r|bash|shell)\b",
    # Frontend/Backend Frameworks
    r"\b(react|reactjs|vue|vuejs|angular|next\.?js|nuxt\.?js|svelte|tailwindcss|bootstrap|sass|less)\b",
    r"\b(node\.?js|express|django|flask|fastapi|spring|spring boot|laravel|dotnet|ruby on rails)\b",
    # Databases & Tools
    r"\b(sql|postgresql|postgres|mysql|mongodb|redis|cassandra|elasticsearch|oracle|sqlite|prisma|sequelize|mongoose)\b",
    # Cloud & DevOps
    r"\b(aws|azure|gcp|google cloud|docker|kubernetes|k8s|jenkins|terraform|ansible|git|github|gitlab|bitbucket|cicd|linux|unix)\b",
    # AI/ML/Data
    r"\b(machine learning|data science|nlp|deep learning|artificial intelligence|pytorch|tensorflow|scikit-learn|pandas|numpy|opencv|keras|llama|openai|llm|huggingface|langchain)\b",
    # APIs & Communication
    r"\b(api|rest|graphql|grpc|websockets|json|xml|microservices|mqtt|amqp|kafka|rabbitmq)\b",
]


# Common non-skill words to ignore (headers, months, locations, etc.)
NON_SKILL_BLACKLIST = {
    "profile", "summary", "experience", "education", "internships", "projects", 
    "achievements", "skills", "contact", "linkedin", "github", "present",
    "january", "february", "march", "april", "may", "june", "july", "august", 
    "september", "october", "november", "december", "present",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "ahmedabad", "gujarat", "india", "university", "college", "school",
    "current", "cgpa", "sem", "year", "total", "address", "phone", "email",
    "name", "various", "multiple", "using", "built", "implemented", "developed",
    "teacher", "bootcamp", "tinkering", "labs", "state", "department", "government",
    "member", "program", "startup", "emerging", "award", "organizing", "since"
}

# Known valid abbreviations (3 chars or fewer)
VALID_SHORT_SKILLS = {
    "aws", "gcp", "nlp", "llm", "api", "sql", "git", "css", "js", "ts", "gpt", 
    "ml", "ai", "db", "os", "vpc", "ec2", "s3", "iam", "sh", "ann", "cnn"
}

def extract_skills(text: str) -> List[str]:
    """Extract strictly technical skills from text with high precision."""
    logger.info("Running Technical Skill Extraction...")
    if not text or not text.strip():
        return []
    
    # Pre-clean: Remove phone numbers, generic dates, and numbers
    # Also separate words that might be attached to dots/slashes
    clean_text = re.sub(r'[\+\d]{2,15}', ' ', text)
    clean_text = re.sub(r'\d+', ' ', clean_text).replace('/', ' ').replace('|', ' ')
    
    text_lower = clean_text.lower()
    skills = set()
    
    # 1. Match explicit Technical Patterns (Highest Confidence)
    for pattern in SKILL_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            val = m.lower() if isinstance(m, str) else m[0].lower()
            if val not in NON_SKILL_BLACKLIST:
                if val in VALID_SHORT_SKILLS:
                    skills.add(val.upper())
                else:
                    skills.add(" ".join(w.capitalize() for w in val.split()))
    
    # 2. Very Restricted Heuristic for Abbreviations (3-5 letters, ALL CAPS in source)
    # This catches things like 'YOLO', 'ANN', etc. if not in patterns
    abbreviations = re.findall(r"\b[A-Z]{3,5}\b", text)
    for s in abbreviations:
        s_lower = s.lower()
        if s_lower in VALID_SHORT_SKILLS:
            skills.add(s.upper())
        elif s_lower not in NON_SKILL_BLACKLIST and len(s) >= 3:
             # Only add if it looks 'techy' (no common vowels etc, or checked vs blacklists)
             if not any(word in NON_SKILL_BLACKLIST for word in s_lower.split()):
                 skills.add(s)

    # 3. Final Filter: ensure we don't have random noise
    result = []
    for s in skills:
        s_low = s.lower()
        if s_low in NON_SKILL_BLACKLIST: continue
        if len(s) < 2: continue
        # If it's a short 2-3 letter word, it MUST be in our valid whitelist
        if len(s) <= 3 and s_low not in VALID_SHORT_SKILLS: continue
        
        result.append(s)
    
    # Limit and return
    return sorted(list(set(result)), key=len)[:25]
