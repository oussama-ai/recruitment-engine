import os
import re
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
from gliner import GLiNER

class ResumeParserNER:
    def __init__(self, csv_path="assets/combined_onet_vocabulary.csv"):
        print("Initialisation du moteur Universel Dual-Engine (GLiNER + PhraseMatcher)...")
        
        # 1. Init Multilingual AI Model
        self.ai_model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        
        # 2. Init Dictionary
        self.nlp = spacy.blank("en") 
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # 3. Build Validation Map
        self.skill_map = {}
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Fichier de taxonomie introuvable: {csv_path}")

        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            raw_val = str(row.get('O_NET_Skill_Or_Tool', '')).strip().lower()
            clean = self.clean_skill(raw_val)
            if clean:
                self.skill_map[clean] = True
        
        # 4. Configure Matcher
        patterns = [self.nlp.make_doc(text) for text in self.skill_map.keys()]
        self.matcher.add("ONET_SKILLS", patterns)
        print(f"{len(self.skill_map)} compétences indexées.")
        
        # 5. Multilingual and Generic Blacklist
        self.skill_blacklist = {
            "science", "programming", "google", "analysis", "tools", "platforms", 
            "student", "engineering", "developpement", "conception", "gestion"
        }

    def clean_skill(self, text: str):
        text = re.sub(r'[^a-zA-Z0-9\s\+\-\#\.]', '', text).strip()
        if len(text) <= 1 or text.isdigit(): return None
        return text

    def _isolate_skills_section(self, text: str) -> str:
        start_patterns = [r"\bTECHNICAL\s+SKILLS\b", r"\bSKILLS\b", r"\bCOMPÉTENCES\b"]
        start_idx = 0
        for pattern in start_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_idx = match.end()
                break
        return text[start_idx:]

    def extract_json_metadata(self, text: str, is_job_description: bool = False) -> dict:
        if not text or str(text).strip() == "":
            return {"skills": [], "experience": 0, "education": []}

        # STEP A: Determine Text Block Scope
        # If it's a job description, scan everything. If it's a resume, isolate the skills section.
        text_block = text if is_job_description else self._isolate_skills_section(text)
        
        # STEP B: Run Dual-Engine Extraction
        ai_entities = self.ai_model.predict_entities(text_block, labels=["skill", "technology", "programming language"])
        doc = self.nlp(text_block)
        matches = self.matcher(doc)
        
        final_skills = set()
        
        # 1. Gather AI Findings (Handles open-vocabulary & global languages)
        for entity in ai_entities:
            clean = self.clean_skill(entity["text"])
            if clean and clean.lower() not in self.skill_blacklist:
                final_skills.add(entity["text"].strip())
                
        # 2. Gather Dictionary Findings (Ensures common terms aren't dropped)
        for match_id, start, end in matches:
            span = doc[start:end]
            clean_match = span.text.strip()
            if clean_match.lower() not in self.skill_blacklist:
                final_skills.add(clean_match)

        # STEP C: Parse Required Experience 
        # (Works for JDs too! e.g., "Requires 3 years of experience" -> 3)
        exp_pattern = re.search(r"(\d+)\s*(?:ans?|années?|years?)\s*(?:d\'?\s*expérience|of\s+experience)?", text, re.IGNORECASE)
        years = int(exp_pattern.group(1)) if exp_pattern else 0

        # STEP D: Parse Education Requirements
        education_entries = []
        degree_regex = r"\b(Cycle d'Ingénieur|Ingénieur|Engineering\s+Degree|Master|Licence|Bachelor|Associate\s+Degree|DUT|DEUST|BTS|Doctorat|Classes Préparatoires|Prepa|Bac\s*\+\s*\d)\b"
        for match in re.finditer(degree_regex, text, re.IGNORECASE):
            degree_name = match.group(0)
            
            if is_job_description:
                # Job descriptions don't have date ranges, they just state the required degree
                duration = "Required"
            else:
                end_pos = match.end()
                context_window = text[end_pos:end_pos + 120]
                date_pattern = r"(\b\d{4}\b|présent|present|en cours|on-going|(?:\b(?:janv|févr|mar|avr|mai|juin|juil|août|sept|oct|nov|déc|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}\b))"
                line_dates = re.findall(date_pattern, context_window, re.IGNORECASE)
                duration = " - ".join(line_dates[:2]) if len(line_dates) >= 2 else (line_dates[0] if line_dates else "En cours")
            
            if not any(e["degree"].lower() == degree_name.lower() for e in education_entries):
                education_entries.append({"degree": degree_name.strip(), "duration": duration.strip()})

        return {
            "skills": sorted(list(final_skills), key=lambda s: s.lower()),
            "experience": years,
            "education": education_entries
        }