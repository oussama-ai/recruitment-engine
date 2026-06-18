# import psycopg2, json
# from ai_engine.embedding import Embedder
# from ai_engine.ner import extract_json_metadata

# def enrich_jobs():
#     """Background worker to process raw data from n8n."""
#     embedder = Embedder()
#     conn = psycopg2.connect("host=localhost dbname=recruitment_db user=postgres password=password")
#     cur = conn.cursor()

#     cur.execute("SELECT id, description FROM jobs WHERE embedding IS NULL")
#     jobs = cur.fetchall()

#     for j_id, desc in jobs:
#         vec = embedder.encode(desc)
#         meta = extract_json_metadata(desc)
#         cur.execute(
#             "UPDATE jobs SET embedding = %s, metadata = %s WHERE id = %s",
#             (vec, json.dumps(meta), j_id)
#         )
#     conn.commit()
#     print(f"Processed {len(jobs)} jobs.")

# if __name__ == "__main__":
#     enrich_jobs()
import psycopg2
import json
import os
from dotenv import load_dotenv
from ai_engine.embedding import Embedder
from ai_engine.ner import extract_json_metadata

# 1. Charger les variables d'environnement (.env)
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def enrich_jobs():
    """Background worker to process raw data from n8n using Neon Cloud DB."""
    if not DB_URL:
        print("❌ Erreur : DATABASE_URL est introuvable dans le fichier .env")
        return

    print("🧠 Initialisation du modèle d'embedding (SBERT)...")
    embedder = Embedder()
    
    try:
        # 2. Connexion sécurisée à la base Neon Cloud
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Récupérer les jobs qui n'ont pas encore été vectorisés
        cur.execute("SELECT id, description FROM jobs WHERE embedding IS NULL OR metadata IS NULL")
        jobs = cur.fetchall()

        if not jobs:
            print("✨ Aucun nouveau job à traiter. Tout est à jour !")
            return

        print(f"🔄 {len(jobs)} jobs trouvés sans embedding/metadata. Début du traitement...")

        for j_id, desc in jobs:
            if not desc:
                continue
            
            # Génération de l'embedding (SBERT) et extraction du JSON (spaCy NER)
            vec = embedder.encode(desc)
            meta = extract_json_metadata(desc)
            
            # Mise à jour de la ligne dans Neon
            # Note : str(vec) transforme la liste [0.1, 0.2] en '[0.1, 0.2]' pour pgvector
            cur.execute(
                "UPDATE jobs SET embedding = %s, metadata = %s WHERE id = %s",
                (str(vec), json.dumps(meta), j_id)
            )
        
        # Validation des changements sur le cloud
        conn.commit()
        
        cur.close()
        conn.close()
        print(f"✅ Traitement terminé avec succès. {len(jobs)} jobs mis à jour dans Neon !")

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du worker : {e}")

if __name__ == "__main__":
    enrich_jobs()