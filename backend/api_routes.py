from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from ai_engine.parser import extract_text_from_pdf
from ai_engine.ner import extract_json_metadata
from ai_engine.embedding import Embedder
from ai_engine.ranking import compute_hybrid_score

router = APIRouter()
embedder = Embedder()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/recommend")
async def recommend_jobs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Parse and Vectorize CV
    cv_bytes = await file.read()
    cv_text = extract_text_from_pdf(cv_bytes)
    cv_meta = extract_json_metadata(cv_text)
    cv_vec = embedder.encode(cv_text)

    # 2. Vector Search (Using pgvector <=> operator)
    query = f"""
        SELECT id, title, company, metadata, 1 - (embedding <=> '{cv_vec}') AS sim
        FROM jobs WHERE embedding IS NOT NULL
        ORDER BY sim DESC LIMIT 10
    """
    raw_results = db.execute(query).fetchall()

    # 3. Hybrid Ranking
    recommendations = []
    for r in raw_results:
        job_meta = r[3] if isinstance(r[3], dict) else {}
        h_score = compute_hybrid_score(r[4], cv_meta, job_meta)

        recommendations.append({
            "title": r[1],
            "company": r[2],
            "score": h_score,
            "matched_skills": list(set(cv_meta['skills']).intersection(set(job_meta.get('skills', []))))
        })

    return sorted(recommendations, key=lambda x: x['score'], reverse=True)