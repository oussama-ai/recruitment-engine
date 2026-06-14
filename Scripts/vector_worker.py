import psycopg2, json
from ai_engine.embedding import Embedder
from ai_engine.ner import extract_json_metadata

def enrich_jobs():
    """Background worker to process raw data from n8n."""
    embedder = Embedder()
    conn = psycopg2.connect("host=localhost dbname=recruitment_db user=postgres password=password")
    cur = conn.cursor()

    cur.execute("SELECT id, description FROM jobs WHERE embedding IS NULL")
    jobs = cur.fetchall()

    for j_id, desc in jobs:
        vec = embedder.encode(desc)
        meta = extract_json_metadata(desc)
        cur.execute(
            "UPDATE jobs SET embedding = %s, metadata = %s WHERE id = %s",
            (vec, json.dumps(meta), j_id)
        )
    conn.commit()
    print(f"Processed {len(jobs)} jobs.")

if __name__ == "__main__":
    enrich_jobs()