from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

engine = create_engine(DB_URL)

try:
    with engine.connect() as conn:

        # pgvector
        conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector;")
        )

        conn.commit()

        print("Base Neon connectée avec succès!")
        print("pgvector activé!")

except Exception as e:
    print("Erreur connexion :", e)