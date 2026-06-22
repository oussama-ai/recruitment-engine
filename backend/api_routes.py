# import json
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
#     try: 
#         yield db
#     finally: 
#         db.close()

# @router.post("/recommend")
# async def recommend_jobs(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     # 1. Extraction du texte et isolation des compétences locales (Sans modifier ner.py)
#     cv_bytes = await file.read()
#     cv_text = extract_text_from_pdf(cv_bytes)
#     cv_meta = ner_parser.extract_json_metadata(cv_text)

#     # Conversion propre pour le type pgvector
#     cv_vec_str = str(list(embedder.encode(cv_text))) 

#     # 2. Recherche vectorielle sur Neon PostgreSQL
#     query = text(f"""
#         SELECT id, title, company_name, job_url, metadata, 1 - (embedding <=> '{cv_vec_str}') AS sim
#         FROM jobs WHERE embedding IS NOT NULL
#         ORDER BY sim DESC LIMIT 10
#     """)
#     raw_results = db.execute(query).fetchall()
    
#     # 3. Reranking Hybride avec gestion stricte des index
#     recommendations = []
#     for r in raw_results:
#         job_url = r[3] if r[3] else "#"
#         sim_score = r[5]
        
#         # Sécurité de parsing de metadata
#         job_meta = r[4]
#         if isinstance(job_meta, str):
#             try:
#                 job_meta = json.loads(job_meta)
#             except json.JSONDecodeError:
#                 job_meta = {}
#         elif not isinstance(job_meta, dict):
#             job_meta = {}

#         # Calcul du score hybride
#         h_score = compute_hybrid_score(sim_score, cv_meta, job_meta)

#         # --- NORMALISATION DES SKILLS DU CV ---
#         # On force tout en minuscules pour éviter les conflits de casse (ex: Python vs python)
#         cv_skills = [str(s).strip().lower() for s in cv_meta.get('skills', [])]

#         # --- EXTRACTION ET NORMALISATION DES SKILLS DU JOB ---
#         # On teste plusieurs clés au cas où le JSON de Neon utilise un autre terme
#         possible_keys = ['skills', 'keywords', 'technologies', 'tags', 'requirements']
#         raw_job_skills = []
        
#         for key in possible_keys:
#             if key in job_meta:
#                 if isinstance(job_meta[key], list):
#                     raw_job_skills = job_meta[key]
#                     break
#                 elif isinstance(job_meta[key], str):
#                     # Si les compétences sont stockées sous forme de texte séparé par des virgules
#                     raw_job_skills = [s.strip() for s in job_meta[key].split(',')]
#                     break
        
#         job_skills = [str(s).strip().lower() for s in raw_job_skills]

#         # --- INTERSECTION SÉCURISÉE ---
#         matched_skills = list(set(cv_skills).intersection(set(job_skills)))

#         # --- CODE DE DEBUGGING TEMPORAIRE ---
#         # Regarde ta console Uvicorn quand tu charges un CV pour voir ce qui bloque !
#         print(f"\n--- DEBUG JOB: {r[1]} ---")
#         print(f"Clés trouvées dans metadata Neon : {list(job_meta.keys())}")
#         print(f"Skills du CV (Minuscules) : {cv_skills}")
#         print(f"Skills du Job détectés : {job_skills}")
#         print(f"Intersection finale : {matched_skills}")

#         recommendations.append({
#             "title": r[1],
#             "company": r[2],
#             "url": job_url,
#             "score": h_score,
#             "matched_skills": matched_skills
#         })

#     return sorted(recommendations, key=lambda x: x['score'], reverse=True)
import json
# Ajout de HTTPException pour la gestion propre des erreurs de validation
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
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
    # 1. Lecture sûre des octets du fichier téléchargé
    try:
        cv_bytes = await file.read()
        cv_text = extract_text_from_pdf(cv_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Erreur lors de la lecture physique du PDF : {str(e)}"
        )

    # 🔒 PROTECTION CONTRE LES CV IMAGES / SCANNÉS
    # Si le texte extrait est vide ou ridiculement court (ex: moins de 20 caractères)
    if not cv_text or len(cv_text.strip()) < 20:
        raise HTTPException(
            status_code=422,
            detail="Le document ne contient pas de texte extractible. Assurez-vous que votre CV n'est pas une image aplatie ou un document scanné sans couche OCR."
        )

    try:
        # Poursuite du pipeline IA classique puisque la présence de texte est validée
        cv_meta = ner_parser.extract_json_metadata(cv_text)

        # Conversion propre pour le type pgvector
        cv_vec_str = str(list(embedder.encode(cv_text))) 

        # 2. Recherche vectorielle sur Neon PostgreSQL
        query = text(f"""
            SELECT id, title, company_name, job_url, metadata, 1 - (embedding <=> :cv_vector) AS sim
            FROM jobs WHERE embedding IS NOT NULL
            ORDER BY sim DESC LIMIT 10
        """)
        raw_results = db.execute(query,{"cv_vector": cv_vec_str}).fetchall()
        
        # 3. Reranking Hybride avec gestion stricte des index
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
            cv_skills = [str(s).strip().lower() for s in cv_meta.get('skills', [])]

            # --- EXTRACTION ET NORMALISATION DES SKILLS DU JOB ---
            possible_keys = ['skills', 'keywords', 'technologies', 'tags', 'requirements']
            raw_job_skills = []
            
            for key in possible_keys:
                if key in job_meta:
                    if isinstance(job_meta[key], list):
                        raw_job_skills = job_meta[key]
                        break
                    elif isinstance(job_meta[key], str):
                        raw_job_skills = [s.strip() for s in job_meta[key].split(',')]
                        break
            
            job_skills = [str(s).strip().lower() for s in raw_job_skills]

            # --- INTERSECTION SÉCURISÉE ---
            matched_skills = list(set(cv_skills).intersection(set(job_skills)))

            # --- CODE DE DEBUGGING EN CONSOLE ---
            print(f"\n--- DEBUG JOB: {r[1]} ---")
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

    except Exception as internal_ai_error:
        # En cas d'erreur inattendue des modèles (vecteur corrompu, etc.), on évite le crash 500 brut
        print(f"❌ CRASH INTERNE PIPELINE : {str(internal_ai_error)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors du traitement par l'infrastructure sémantique."
        )