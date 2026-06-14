<<<<<<< Updated upstream
=======
import spacy
from spacy.matcher import PhraseMatcher
import re

# Load Small model (Standard for production speed)
nlp = spacy.load("en_core_web_sm")

# Define Technical Taxonomy
SKILLS_DB = [
    "Python", "Java", "SQL", "React", "Angular", "Docker", "Kubernetes",
    "FastAPI", "NLP", "Machine Learning", "PyTorch", "TensorFlow",
    "Azure", "AWS", "NoSQL", "PostgreSQL", "Data Science"
] #demo list, should be expanded for real use

DEGREE_KEYWORDS = [
    r"Engineering Degree", r"Ingénieur", r"Master", r"Licence", 
    r"Bachelor's?", r"Associate Degree", r"Doctorate", r"PhD", 
    r"Bac\s*\+\s*\d", r"Professional Bachelor"
]

def extract_json_metadata(text):
    """Extracts structured JSON entities from text."""
    doc = nlp(text)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in SKILLS_DB]
    matcher.add("SKILLS", patterns)

    # Extract Skills
    found_skills = list(set([doc[start:end].text for _, start, end in matcher(doc)]))

    # Extract Experience (Heuristic: Look for numbers near 'years' or 'ans')
    exp_pattern = re.search(r'(\d+)\+?\s*(years?|ans)', text, re.IGNORECASE)
    years = int(exp_pattern.group(1)) if exp_pattern else 0

    # --- REFINED EDUCATION EXTRACTION ---
    education_entries = []
    degree_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(d) for d in DEGREE_KEYWORDS]
    degree_matcher.add("DEGREE", patterns)

    # 3. Find all matches in the text
    matches = degree_matcher(doc)
    
    for match_id, start, end in matches:
        # Get the degree text found
        degree_name = doc[start:end].text
        
        # 4. Look for dates NEAR this match (e.g., 15 words after the degree)
        # We look at the window of text following the degree name
        window_start = end
        window_end = min(end + 15, len(doc))
        context_window = doc[window_start:window_end].text
        
        # Regex just for the date within this small window
        date_pattern = r'(\b\d{4}\b|Present|(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\b))'
        line_dates = re.findall(date_pattern, context_window, re.IGNORECASE)
        
        duration = " - ".join(line_dates) if line_dates else "Date Not Found"
        
        education_entries.append({
            "degree": degree_name.title(),
            "duration": duration
        })

    return {
        "skills": found_skills,
        "experience": years,
        "education": education_entries
    }
>>>>>>> Stashed changes
