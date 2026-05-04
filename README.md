📄 Recruitment Engine: 

AI-Powered Job Matching System An end-to-end automated pipeline designed to bridge the gap between job seekers and Moroccan IT opportunities. This system uses n8n for automated web scraping, SBERT for semantic embeddings, and Streamlit for a seamless user experience.

🏗️ Project ArchitectureThe engine is built on a modular architecture to ensure scalability and separation of concerns:

Data Ingestion (/n8n): Automated workflows that trigger Apify scrapers to collect job offers from LinkedIn and Google Jobs, storing them in a PostgreSQL database.

AI Core (/ai_engine): The "brain" of the project. It handles PDF parsing, Named Entity Recognition (NER) for skills, and generates semantic embeddings using Sentence-BERT.

API Layer (/backend): A FastAPI server that acts as a bridge between the database, the AI model, and the user interface.

User Interface (/frontend): A Streamlit application for candidates to upload CVs and visualize matching scores in real-time.

🚀 Tech StackOrchestration: 

n8nData Extraction: Apify API (LinkedIn/Google Jobs Scraper)

Database: PostgreSQL (with pgvector for similarity search)

NLP & Embeddings: Sentence-Transformers (SBERT), spaCy, PyMuPDFWeb 

Frameworks: FastAPI (Backend), Streamlit (Frontend)

📂 Directory StructurePlaintext/recruitment-engine

├── n8n/                # Workflows for scraping and DB sync

├── backend/            # FastAPI entry points and DB models

├── ai_engine/          # SBERT logic, NER, and PDF parsing

├── frontend/           # Streamlit UI (Upload & Dashboard)

├── scripts/            # Database initialization scripts

└── requirements.txt    # Project dependencies

🛠️ Installation & Setup

1. Prerequisites
   
   Python 3.10+
   
   PostgreSQL 14+
   
   n8n (Self-hosted or Cloud)2.

2. Install Dependencies
   
   pip install -r requirements.txt

   python -m spacy download fr_core_news_lg

3. Database Initialization
   
   python scripts/init_db.py
   
4. Import n8n Workflow

   Open n8n.
   
   Import n8n/workflows.json.
   
   Update your Apify API Token and PostgreSQL Credentials.
   
5. Launch the Application
   
  # Start Backend
  
  uvicorn backend.main:app --reload
  
  # Start Frontend (New terminal)
  
  streamlit run frontend/home.py
