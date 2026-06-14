def compute_hybrid_score(semantic_sim, cv_meta, job_meta):
    """
    Score Calculation:
    60% Semantic Similarity (Context)
    40% Skill Matching (Strict keywords)
    """
    job_skills = set(job_meta.get('skills', []))
    cv_skills = set(cv_meta.get('skills', []))

    if not job_skills:
        return float(semantic_sim)

    # Skill overlap
    intersection = cv_skills.intersection(job_skills)
    skill_score = len(intersection) / len(job_skills)

    # Weighted Result
    final_score = (0.6 * float(semantic_sim)) + (0.4 * skill_score)
    return round(final_score, 4)