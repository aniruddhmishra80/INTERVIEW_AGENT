from langchain_google_genai import ChatGoogleGenerativeAI

def generate_report(score_history: list, skills_covered: list) -> dict:
    if not score_history:
        return {"overall_score": 0, "per_skill_scores": {}, "strengths": [], "gaps": [], "recommendation": "No Data", "summary": "No questions were answered."}

    per_skill_scores = {}
    for entry in score_history:
        skill = entry["skill"]
        if skill not in per_skill_scores:
            per_skill_scores[skill] = []
        per_skill_scores[skill].append(entry["score"])
        
    avg_per_skill = {k: sum(v)/len(v) for k, v in per_skill_scores.items()}
    overall_score = sum(avg_per_skill.values()) / len(avg_per_skill) if avg_per_skill else 0
    
    strengths = [k for k, v in avg_per_skill.items() if v > 7][:3]
    gaps = [k for k, v in avg_per_skill.items() if v < 5][:3]
    
    if overall_score >= 7.5:
        recommendation = "Strong Hire"
    elif overall_score >= 5.5:
        recommendation = "Hire"
    else:
        recommendation = "No Hire"
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    prompt = f"""Generate a concise one-paragraph summary of this interview performance.
Overall Score: {overall_score}/10
Strengths: {strengths}
Gaps: {gaps}
Recommendation: {recommendation}"""
    try:
        summary = llm.invoke(prompt).content.strip()
    except Exception as e:
        summary = f"Could not generate summary. Reason: {str(e)}"
    
    return {
        "overall_score": round(overall_score, 1),
        "per_skill_scores": {k: round(v, 1) for k, v in avg_per_skill.items()},
        "strengths": strengths,
        "gaps": gaps,
        "recommendation": recommendation,
        "summary": summary
    }
