# from fastapi import APIRouter, UploadFile, File, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy import text 
# from .database import SessionLocal
# from ai_engine.parser import extract_text_from_pdf
# from ai_engine.ner import ResumeParserNER
# from ai_engine.embedding import Embedder
# from ai_engine.ranking import compute_hybrid_score

# router = APIRouter()
# embedder = Embedder()
# ner_parser = ResumeParserNER()

# def get_db():
#     db = SessionLocal()
#     try: yield db
#     finally: db.close()

# @router.post("/recommend")
# async def recommend_jobs(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     # # 1. Parse and Vectorize CV
#     # cv_bytes = await file.read()
#     # cv_text = extract_text_from_pdf(cv_bytes)
#     # cv_meta = extract_json_metadata(cv_text)
#     # cv_vec = embedder.encode(cv_text)

#     # # 2. Vector Search (Using pgvector <=> operator)
#     # query = f"""
#     #     SELECT id, title, company_name, metadata, 1 - (embedding <=> '{cv_vec}') AS sim
#     #     FROM jobs WHERE embedding IS NOT NULL
#     #     ORDER BY sim DESC LIMIT 10
#     # """
#     # raw_results = db.execute(query).fetchall()
#     # 1. Parse and Vectorize CV
#     cv_bytes = await file.read()
#     cv_text = extract_text_from_pdf(cv_bytes)
#     cv_meta = ner_parser.extract_json_metadata(cv_text)

#         # Conversion propre pour pgvector '[0.1, 0.2, ...]'
#     cv_vec_str = str(list(embedder.encode(cv_text))) 

#         # 2. Vector Search (Using pgvector <=> operator avec text())
#     query = text(f"""
#             SELECT id, title, company_name, job_url, metadata, 1 - (embedding <=> '{cv_vec_str}') AS sim
#             FROM jobs WHERE embedding IS NOT NULL
#             ORDER BY sim DESC LIMIT 10
#         """)
#     raw_results = db.execute(query).fetchall()
#     # 3. Hybrid Ranking
#     recommendations = []
#     for r in raw_results:
#         job_meta = r[3] if isinstance(r[3], dict) else {}
#         h_score = compute_hybrid_score(r[4], cv_meta, job_meta)

#         recommendations.append({
#             "title": r[1],
#             "company": r[2],
#             "url": r[4],
#             "score": h_score,
#             "matched_skills": list(set(cv_meta['skills']).intersection(set(job_meta.get('skills', []))))
#         })

#     return sorted(recommendations, key=lambda x: x['score'], reverse=True)
import json
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text 
from .database import SessionLocal
from ai_engine.parser import extract_text_from_pdf
from ai_engine.ner import ResumeParserNER
from ai_engine.embedding import Embedder
from ai_engine.ranking import compute_hybrid_score

router = APIRouter()
embedder = Embedder()
ner_parser = ResumeParserNER()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/recommend")
async def recommend_jobs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Extraction du texte et isolation des compétences locales (Sans modifier ner.py)
    cv_bytes = await file.read()
    cv_text = extract_text_from_pdf(cv_bytes)
    cv_meta = ner_parser.extract_json_metadata(cv_text)

    # Conversion propre pour le type pgvector
    cv_vec_str = str(list(embedder.encode(cv_text))) 

    # 2. Recherche vectorielle sur Neon PostgreSQL
    query = text(f"""
        SELECT id, title, company_name, job_url, metadata, 1 - (embedding <=> '{cv_vec_str}') AS sim
        FROM jobs WHERE embedding IS NOT NULL
        ORDER BY sim DESC LIMIT 10
    """)
    raw_results = db.execute(query).fetchall()
    
    # 3. Reranking Hybride avec gestion stricte des index
    # recommendations = []
    # for r in raw_results:
    #     # Correspondance exacte des index suite à l'ajout de job_url:
    #     # r[0]=id, r[1]=title, r[2]=company_name, r[3]=job_url, r[4]=metadata, r[5]=sim
        
    #     job_url = r[3] if r[3] else "#"
    #     sim_score = r[5]
        
    #     # Sécurité pour parser le dictionnaire metadata (Neon peut le renvoyer sous forme de String)
    #     job_meta = r[4]
    #     if isinstance(job_meta, str):
    #         try:
    #             job_meta = json.loads(job_meta)
    #         except json.JSONDecodeError:
    #             job_meta = {}
    #     elif not isinstance(job_meta, dict):
    #         job_meta = {}

    #     # Calcul du score hybride (On passe enfin la similarité numérique r[5] !)
    #     h_score = compute_hybrid_score(sim_score, cv_meta, job_meta)

    #     # Calcul de l'intersection réelle des compétences (Maintenant que job_meta est valide)
    #     cv_skills = set(cv_meta.get('skills', []))
    #     job_skills = set(job_meta.get('skills', []))
    #     matched_skills = list(cv_skills.intersection(job_skills))

    #     recommendations.append({
    #         "title": r[1],
    #         "company": r[2],
    #         "url": job_url,
    #         "score": h_score,
    #         "matched_skills": matched_skills
    #     })

    # # Tri final décroissant sur le score hybride réajusté
    # return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    # 3. Reranking Hybride avec normalisation des compétences
    recommendations = []
    for r in raw_results:
        job_url = r[3] if r[3] else "#"
        sim_score = r[5]
        
        # Sécurité de parsing de metadata
        job_meta = r[4]
        if isinstance(job_meta, str):
            try:
                job_meta = json.loads(job_meta)
            except json.JSONDecodeError:
                job_meta = {}
        elif not isinstance(job_meta, dict):
            job_meta = {}

        # Calcul du score hybride
        h_score = compute_hybrid_score(sim_score, cv_meta, job_meta)

        # --- NORMALISATION DES SKILLS DU CV ---
        # On force tout en minuscules pour éviter les conflits de casse (ex: Python vs python)
        cv_skills = [str(s).strip().lower() for s in cv_meta.get('skills', [])]

        # --- EXTRACTION ET NORMALISATION DES SKILLS DU JOB ---
        # On teste plusieurs clés au cas où le JSON de Neon utilise un autre terme
        possible_keys = ['skills', 'keywords', 'technologies', 'tags', 'requirements']
        raw_job_skills = []
        
        for key in possible_keys:
            if key in job_meta:
                if isinstance(job_meta[key], list):
                    raw_job_skills = job_meta[key]
                    break
                elif isinstance(job_meta[key], str):
                    # Si les compétences sont stockées sous forme de texte séparé par des virgules
                    raw_job_skills = [s.strip() for s in job_meta[key].split(',')]
                    break
        
        job_skills = [str(s).strip().lower() for s in raw_job_skills]

        # --- INTERSECTION SÉCURISÉE ---
        matched_skills = list(set(cv_skills).intersection(set(job_skills)))

        # --- CODE DE DEBUGGING TEMPORAIRE ---
        # Regarde ta console Uvicorn quand tu charges un CV pour voir ce qui bloque !
        print(f"\n--- DEBUG JOB: {r[1]} ---")
        print(f"Clés trouvées dans metadata Neon : {list(job_meta.keys())}")
        print(f"Skills du CV (Minuscules) : {cv_skills}")
        print(f"Skills du Job détectés : {job_skills}")
        print(f"Intersection finale : {matched_skills}")

        recommendations.append({
            "title": r[1],
            "company": r[2],
            "url": job_url,
            "score": h_score,
            "matched_skills": matched_skills
        })

    return sorted(recommendations, key=lambda x: x['score'], reverse=True)