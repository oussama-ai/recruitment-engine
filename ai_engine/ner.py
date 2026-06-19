# import spacy
# from spacy.matcher import PhraseMatcher
# import re

# # Load Small model (Standard for production speed)
# nlp = spacy.load("en_core_web_sm")

# # Define Technical Taxonomy
# SKILLS_DB = [
#     "Python", "Java", "SQL", "React", "Angular", "Docker", "Kubernetes",
#     "FastAPI", "NLP", "Machine Learning", "PyTorch", "TensorFlow",
#     "Azure", "AWS", "NoSQL", "PostgreSQL", "Data Science"
# ] #demo list, should be expanded for real use

# DEGREE_KEYWORDS = [
#     r"Engineering Degree", r"Ingénieur", r"Master", r"Licence", 
#     r"Bachelor's?", r"Associate Degree", r"Doctorate", r"PhD", 
#     r"Bac\s*\+\s*\d", r"Professional Bachelor"
# ]

# def extract_json_metadata(text):
#     """Extracts structured JSON entities from text."""
#     doc = nlp(text)
#     matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
#     patterns = [nlp.make_doc(skill) for skill in SKILLS_DB]
#     matcher.add("SKILLS", patterns)

#     # Extract Skills
#     found_skills = list(set([doc[start:end].text for _, start, end in matcher(doc)]))

#     # Extract Experience (Heuristic: Look for numbers near 'years' or 'ans')
#     exp_pattern = re.search(r'(\d+)\+?\s*(years?|ans)', text, re.IGNORECASE)
#     years = int(exp_pattern.group(1)) if exp_pattern else 0

#     # --- REFINED EDUCATION EXTRACTION ---
#     education_entries = []
#     degree_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
#     patterns = [nlp.make_doc(d) for d in DEGREE_KEYWORDS]
#     degree_matcher.add("DEGREE", patterns)

#     # 3. Find all matches in the text
#     matches = degree_matcher(doc)
    
#     for match_id, start, end in matches:
#         # Get the degree text found
#         degree_name = doc[start:end].text
        
#         # 4. Look for dates NEAR this match (e.g., 15 words after the degree)
#         # We look at the window of text following the degree name
#         window_start = end
#         window_end = min(end + 15, len(doc))
#         context_window = doc[window_start:window_end].text
        
#         # Regex just for the date within this small window
#         date_pattern = r'(\b\d{4}\b|Present|(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\b))'
#         line_dates = re.findall(date_pattern, context_window, re.IGNORECASE)
        
#         duration = " - ".join(line_dates) if line_dates else "Date Not Found"
        
#         education_entries.append({
#             "degree": degree_name.title(),
#             "duration": duration
#         })

#     return {
#         "skills": found_skills,
#         "experience": years,
#         "education": education_entries
#     }
import spacy
import re

class ResumeParserNER:
    def __init__(self):
        print("Chargement des modèles linguistiques locaux...")
        # On charge les deux modèles légers en mémoire pour éviter les lenteurs d'initialisation
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_fr = spacy.load("fr_core_news_sm")

    def _detect_language(self, text: str) -> str:
        """Détecte localement si le CV est en français ou en anglais par calcul de score."""
        text_lower = text.lower()
        
        # Indicateurs structurels forts
        fr_words = ["compétences", "expérience", "formation", "études", "projets", "langues", "connaissances"]
        en_words = ["skills", "experience", "education", "projects", "languages", "summary", "management"]
        
        fr_score = sum(1 for word in fr_words if word in text_lower)
        en_score = sum(1 for word in en_words if word in text_lower)
        
        return "fr" if fr_score >= en_score else "en"

    def extract_json_metadata(self, text: str) -> dict:
        """Extracts structured JSON metadata automatically handling French and English CVs."""
        
        # --- 1. DÉTECTION DE LA LANGUE & CONFIGURATION ---
        lang = self._detect_language(text)
        nlp = self.nlp_fr if lang == "fr" else self.nlp_en
        
        # Fusion des labels d'exclusion (spaCy EN utilise PERSON/GPE, spaCy FR utilise PER/LOC)
        exclude_labels = ["PERSON", "PER", "GPE", "LOC", "DATE", "MONEY", "CARDINAL"]
        
        doc = nlp(text)

        # --- 2. LOCAL DYNAMIC SKILLS EXTRACTION (SECTION-AWARE) ---
        skills_headers = r"\b(skills|competences|compétences|technical skills|expertises|technologies|hard skills|tools|outils)\b"
        next_sections = r"\b(experience|expérience|education|éducation|formation|projects|projets|languages|langues|interests|passions|summary|professional|parcours)\b"
        
        skills_text = ""
        match = re.search(f"{skills_headers}(.*?)(?={next_sections}|$)", text, re.IGNORECASE | re.DOTALL)
        
        if match:
            skills_text = match.group(2)
        
        target_doc = nlp(skills_text) if skills_text.strip() else doc
        
        # Collecte des entités nommées à exclure (Lieux, Noms de famille, Dates)
        exclude_ents = set()
        for ent in doc.ents:
            if ent.label_ in exclude_labels:
                for token in ent:
                    exclude_ents.add(token.text.lower())

        found_skills = []
        
        # Extraction par groupes nominaux (Noun Chunks)
        for chunk in target_doc.noun_chunks:
            clean_chunk = chunk.text.strip().lower()
            # Nettoyage des résidus de mise en page (Barres, tirets, parenthèses pour pandas)
            clean_chunk = re.sub(r'[\|\-\$\d\t\n\(\)]', '', clean_chunk).strip()
            
            if len(clean_chunk.split()) <= 3 and len(clean_chunk) > 1:
                if not any(word in exclude_ents for word in clean_chunk.split()):
                    if not chunk.root.is_stop and chunk.root.pos_ in ["PROPN", "NOUN"]:
                        # Mots génériques à filtrer selon la langue si fallback global activé
                        ignored_words = ['work', 'job', 'system', 'project', 'application', 'travail', 'projet', 'système']
                        if skills_text.strip() or clean_chunk not in ignored_words:
                            found_skills.append(clean_chunk)

        # Extraction des mots isolés essentiels (Ex: Python, Docker, SQL)
        for token in target_doc:
            token_lower = token.text.lower()
            if token.pos_ == "PROPN" and not token.is_stop and token_lower not in exclude_ents:
                if len(token_lower) > 1:
                    if skills_text.strip() or token_lower not in ['work', 'job', 'project', 'projet', 'travail']:
                        found_skills.append(token_lower)

        final_skills = list(set(found_skills))

        # --- 3. EXTRACTION DE L'EXPÉRIENCE (RegEx Hybride FR/EN) ---
        exp_pattern = re.search(r'(\d+)\+?\s*(years?|ans)', text, re.IGNORECASE)
        years = int(exp_pattern.group(1)) if exp_pattern else 0

        # --- 4. REFINED EDUCATION EXTRACTION (RegEx Mots-Clés FR/EN) ---
        education_entries = []
        degree_regex = r"\b(Engineering Degree|Ingénieur|Master|Licence|Bachelor(?:'s)?|Associate Degree|Doctorate|PhD|Bac\s*\+\s*\d|Professional Bachelor|Diplôme|Doctorat|Classes Préparatoires|Prepa)\b"
        
        for match in re.finditer(degree_regex, text, re.IGNORECASE):
            degree_name = match.group(0)
            end_pos = match.end()
            
            context_window = text[end_pos : end_pos + 100]
            # Capture des dates standards (2024, Jan 2024, Oct. 2023, Présent, Present)
            date_pattern = r'(\b\d{4}\b|Present|Présent|(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Octobre|Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Novembre|Décembre)[a-z]*\.?\s*\d{4}\b))'
            line_dates = re.findall(date_pattern, context_window, re.IGNORECASE)
            
            duration = " - ".join(line_dates) if line_dates else "Date Not Found"
            
            education_entries.append({
                "degree": degree_name.title(),
                "duration": duration
            })

        return {
            "skills": final_skills,
            "experience": years,
            "education": education_entries
        }