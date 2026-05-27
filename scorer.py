import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_score(answer: str, ideal: str) -> float:
    emb1 = model.encode([answer])
    emb2 = model.encode([ideal])
    sim = cosine_similarity(emb1, emb2)[0][0]
    return float(sim)

def keyword_score(answer: str, keywords: list) -> float:
    if not keywords:
        return 1.0
    ans_lower = answer.lower()
    count = sum(1 for kw in keywords if kw.lower() in ans_lower)
    return count / len(keywords)

def llm_score(question: str, answer: str, rubric: str) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    prompt = f"""You are evaluating an interview answer. Question: {question}. Ideal answer criteria: {rubric}. Candidate said: {answer}. Score 1-10 where 10 = complete, accurate, uses correct terminology. Return ONLY: score: N, feedback: one sentence."""
    response = llm.invoke(prompt).content
    
    score = 5.0
    feedback = ""
    try:
        score_match = re.search(r"score:\s*(\d+)", response, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
        
        feedback_match = re.search(r"feedback:\s*(.*)", response, re.IGNORECASE)
        if feedback_match:
            feedback = feedback_match.group(1)
    except Exception as e:
        print(f"Error parsing LLM score: {e}")
        
    return {"score": score, "feedback": feedback.strip()}

def final_score(answer: str, ideal: str, keywords: list, question: str, rubric: str) -> dict:
    sem = semantic_score(answer, ideal)
    kw = keyword_score(answer, keywords)
    llm_res = llm_score(question, answer, rubric)
    
    llm_val = llm_res["score"] / 10.0
    final_val = (sem * 0.3) + (kw * 0.2) + (llm_val * 0.5)
    final_10 = final_val * 10
    
    needs_review = False
    if abs(llm_res["score"] - (sem * 10)) > 2.0:
        needs_review = True
        
    return {
        "final_score": round(final_10, 1),
        "semantic_score": round(sem * 10, 1),
        "keyword_score": round(kw * 10, 1),
        "llm_score": llm_res["score"],
        "feedback": llm_res["feedback"],
        "needs_review": needs_review
    }
