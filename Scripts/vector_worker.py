# import psycopg2
# import json
# import os
# from dotenv import load_dotenv
# from ai_engine.embedding import Embedder
# from ai_engine.ner import ResumeParserNER

# # 1. Charger les variables d'environnement (.env)
# ner_parser = ResumeParserNER()
# load_dotenv()
# DB_URL = os.getenv("DATABASE_URL")

# def enrich_jobs():
#     """Background worker to process raw data from n8n using Neon Cloud DB."""
#     if not DB_URL:
#         print("❌ Erreur : DATABASE_URL est introuvable dans le fichier .env")
#         return

#     print("🧠 Initialisation du modèle d'embedding (SBERT)...")
#     embedder = Embedder()
    
#     try:
#         # 2. Connexion sécurisée à la base Neon Cloud
#         conn = psycopg2.connect(DB_URL)
#         cur = conn.cursor()

#         # Récupérer les jobs qui n'ont pas encore été vectorisés
#         cur.execute("SELECT id, description FROM jobs WHERE embedding IS NULL OR metadata IS NULL")
#         jobs = cur.fetchall()

#         if not jobs:
#             print("✨ Aucun nouveau job à traiter. Tout est à jour !")
#             return

#         print(f"🔄 {len(jobs)} jobs trouvés sans embedding/metadata. Début du traitement...")

#         for j_id, desc in jobs:
#             if not desc:
#                 continue
            
#             # Génération de l'embedding (SBERT) et extraction du JSON (spaCy NER)
#             vec = embedder.encode(desc)
#             meta = ner_parser.extract_json_metadata(desc, is_job_description=True)
            
#             # Mise à jour de la ligne dans Neon
#             # Note : str(vec) transforme la liste [0.1, 0.2] en '[0.1, 0.2]' pour pgvector
#             cur.execute(
#                 "UPDATE jobs SET embedding = %s, metadata = %s WHERE id = %s",
#                 (str(vec), json.dumps(meta), j_id)
#             )
        
#         # Validation des changements sur le cloud
#         conn.commit()
        
#         cur.close()
#         conn.close()
#         print(f"✅ Traitement terminé avec succès. {len(jobs)} jobs mis à jour dans Neon !")

#     except Exception as e:
#         print(f"❌ Erreur lors de l'exécution du worker : {e}")

# if __name__ == "__main__":
#     enrich_jobs()
import os
import sys
# Bulletproof path routing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import json
from dotenv import load_dotenv
from ai_engine.ner import ResumeParserNER

print("⏳ Initialisation du moteur Dual-Engine NER...")
ner_parser = ResumeParserNER()

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def enrich_jobs_metadata_batched():
    if not DB_URL:
        print("❌ Erreur : DATABASE_URL introuvable.")
        return
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        cur.execute("SELECT id, description FROM jobs WHERE metadata IS NULL")
        jobs = cur.fetchall()

        if not jobs:
            print("✨ Tout est déjà à jour !")
            cur.close()
            conn.close()
            return

        print(f"🔄 Traitement de {len(jobs)} jobs...")
        
        success_count = 0
        
        for j_id, desc in jobs:
            if not desc or str(desc).strip() == "":
                continue
            
            try:
                meta = ner_parser.extract_json_metadata(desc, is_job_description=True)
                
                # Prépare la requête en mémoire sans forcer la base cloud à écrire immédiatement
                cur.execute(
                    "UPDATE jobs SET metadata = %s WHERE id = %s",
                    (json.dumps(meta), j_id)
                )
                success_count += 1
                if success_count % 10 == 0:
                    print(f"🔹 En cours : {success_count}/{len(jobs)} analysés...")
                    
            except Exception as job_error:
                print(f"⚠️ Job {j_id} ignoré : {job_error}")
                continue
        
        # UNE SEULE transaction réseau pour sauvegarder l'intégralité du lot
        print("🚀 Envoi du lot complet à Neon Cloud...")
        conn.commit() 
        
        cur.close()
        conn.close()
        print(f"✅ Terminé ! {success_count} jobs synchronisés en une seule passe.")

    except Exception as e:
        print(f"❌ Erreur critique : {e}")

if __name__ == "__main__":
    enrich_jobs_metadata_batched()