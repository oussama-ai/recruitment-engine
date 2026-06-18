import fitz  # PyMuPDF
import re

def clean_text(text):
    """Production-grade text cleaning for NLP."""
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespaces
    text = re.sub(r'http\S+|[\w\.-]+@[\w\.-]+', '', text)  # Remove URLs and Emails
    return text.strip()

def extract_text_from_pdf(pdf_stream):
    """Extracts and cleans text from PDF bytes."""
    try:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        raw_text = " ".join([page.get_text() for page in doc])
        return clean_text(raw_text)
    except Exception as e:
        print(f"Parser Error: {e}")
        return ""