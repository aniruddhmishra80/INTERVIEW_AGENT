import pypdf
import pdfplumber
import pytesseract
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

def extract_text_from_pdf(file_obj) -> str:
    text = ""
    try:
        reader = pypdf.PdfReader(file_obj)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"pypdf error: {e}")
        
    if len(text.strip()) < 100:
        try:
            file_obj.seek(0)
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber error: {e}")
            
    return text.strip()

def _get_llm(temperature=0.0):
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)

def extract_resume_skills(text: str) -> dict:
    prompt = """Extract all technical skills, tools, programming languages, frameworks, and project names from this resume. Return ONLY valid JSON in this exact format: {"name": "Candidate Name", "skills": [], "projects": [{"name": "Project", "tech": []}], "experience_years": 0}"""
    llm = _get_llm()
    messages = [
        ("system", prompt),
        ("human", text)
    ]
    try:
        response = llm.invoke(messages).content
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except Exception:
        # Retry ONCE
        retry_prompt = "Return ONLY raw JSON, no markdown, no explanation, no backticks."
        messages = [
            ("system", prompt + "\n" + retry_prompt),
            ("human", text)
        ]
        try:
            response2 = llm.invoke(messages).content
            cleaned2 = response2.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned2)
        except:
            return {"name": "Unknown", "skills": [], "projects": [], "experience_years": 0}

def extract_jd_requirements(text: str) -> dict:
    prompt = """Extract required skills, preferred skills, role title, and key responsibilities. Return ONLY valid JSON: {"role": "Role Title", "required_skills": [], "preferred_skills": [], "responsibilities": []}"""
    llm = _get_llm()
    messages = [
        ("system", prompt),
        ("human", text)
    ]
    try:
        response = llm.invoke(messages).content
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except Exception:
        retry_prompt = "Return ONLY raw JSON, no markdown, no explanation, no backticks."
        messages = [
            ("system", prompt + "\n" + retry_prompt),
            ("human", text)
        ]
        try:
            response2 = llm.invoke(messages).content
            cleaned2 = response2.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned2)
        except:
            return {"role": "Unknown", "required_skills": [], "preferred_skills": [], "responsibilities": []}
