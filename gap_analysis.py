def compute_gap(resume_skills: list, jd_skills: list) -> dict:
    res_set = set([s.lower().strip() for s in resume_skills])
    jd_set = set([s.lower().strip() for s in jd_skills])
    
    matched = res_set.intersection(jd_set)
    missing = jd_set.difference(res_set)
    bonus = res_set.difference(jd_set)
    
    score = len(matched) / len(jd_set) if len(jd_set) > 0 else 1.0
    
    return {
        "matched": list(matched),
        "missing": list(missing),
        "bonus": list(bonus),
        "match_score": score
    }
