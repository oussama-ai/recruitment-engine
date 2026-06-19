import sys 
import os
sys.path.append(os.getcwd())
from ai_engine.parser import clean_text
from ai_engine.parser import extract_text_from_pdf
from ai_engine.ner import ResumeParserNER

ner_parser = ResumeParserNER()

def run_cv_pipeline(pdf_stream):
    """Runs the entire CV parsing and NER pipeline."""
    if not os.path.exists(pdf_stream):
        raise ValueError("Input must be a PDF stream.")
    with open(pdf_stream, 'rb') as f:
        pdf_bytes = f.read()
    
    raw_text = extract_text_from_pdf(pdf_bytes)
    print("\n[STEP 1: PARSER RESULT]")
    print(raw_text[:500] + "...") # Print first 500 characters
    cleaned_text = clean_text(raw_text)
    print("\n[STEP 2: CLEANED TEXT]")
    print(cleaned_text[:500] + "...") # Print first 500 characters
    metadata = ner_parser.extract_json_metadata(cleaned_text)
    print("\n[STEP 3: EXTRACTED METADATA]")
    return metadata

if __name__ == "__main__":
    # Example usage with a sample PDF path
    pdf_path = r"C:\Users\Lenovo\Documents\ia\ML\ML practice\CVEN_Oussama_Lebyed_EN_2026.pdf"  # Replace with actual PDF path
    try:
        result = run_cv_pipeline(pdf_path)
        print(result)
    except Exception as e:
        print(f"Error processing CV: {e}")