"""
keyword_extractor.py
NLP-based keyword and skill extraction from resume and JD text.
Uses TF-IDF + a curated tech skill vocabulary for ATS simulation.
"""
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Curated skill vocabulary ──────────────────────────────────────────────────
TECH_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "r", "scala", "sql", "bash", "shell",
    # Frameworks / Libraries
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "spring", "spring boot", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "streamlit", "langchain",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "jenkins", "github actions", "ansible",
    # AI / ML
    "machine learning", "deep learning", "nlp", "llm", "generative ai",
    "rag", "prompt engineering", "computer vision", "reinforcement learning",
    "transformers", "bert", "gpt", "openai", "gemini",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "firebase",
    "dynamodb", "cassandra",
    # Tools / Concepts
    "git", "github", "jira", "agile", "scrum", "rest api", "graphql",
    "microservices", "oop", "data structures", "algorithms",
    # Soft skills (common in JDs)
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "collaboration",
}


def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_ats_keywords(text: str) -> list[str]:
    """Return skill keywords found in text (from curated vocab)."""
    cleaned = _clean(text)
    found = []
    for skill in TECH_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, cleaned):
            found.append(skill)
    return sorted(set(found))


def extract_tfidf_keywords(text: str, top_n: int = 20) -> list[str]:
    """Extract top-N keywords using TF-IDF on the given text."""
    sentences = [s.strip() for s in re.split(r"[.\n]", text) if len(s.strip()) > 10]
    if not sentences:
        return []
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=200,
        )
        vectorizer.fit_transform(sentences)
        scores = zip(
            vectorizer.get_feature_names_out(),
            vectorizer.idf_,
        )
        ranked = sorted(scores, key=lambda x: x[1])
        return [kw for kw, _ in ranked[:top_n]]
    except Exception:
        return []


def compute_keyword_match(resume_text: str, jd_text: str) -> dict:
    """
    Compare resume keywords vs JD keywords.
    Returns matched, missing, and match_score (%).
    """
    resume_kws = set(extract_ats_keywords(resume_text))
    jd_kws = set(extract_ats_keywords(jd_text))

    if not jd_kws:
        return {"matched": [], "missing": [], "match_score": 0, "jd_keywords": []}

    matched = resume_kws & jd_kws
    missing = jd_kws - resume_kws
    score = round(len(matched) / len(jd_kws) * 100, 1)

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "match_score": score,
        "jd_keywords": sorted(jd_kws),
    }
