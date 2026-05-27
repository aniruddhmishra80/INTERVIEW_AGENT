from langchain_core.prompts import PromptTemplate

def build_system_prompt(gap_report: dict, candidate_name: str, projects: list, difficulty: str = "normal") -> PromptTemplate:
    matched = gap_report.get("matched", [])
    missing = gap_report.get("missing", [])
    
    system_instruction = f"""You are a senior technical interviewer at ADP. You are interviewing {candidate_name}.
Their confirmed skills: {', '.join(matched) if matched else 'None'}.
Skills required by the JD they are missing: {', '.join(missing) if missing else 'None'}.
Their projects: {projects}.
Rules:
- Ask harder questions on matched skills (they claimed to know these)
- Ask targeted questions on missing skills (JD requires these)
- Reference their actual project names in questions
- Do NOT ask about technologies not in either document
- Ask one question at a time
- Keep each question under 3 sentences"""

    if difficulty == "hard":
        system_instruction += "\nAsk edge cases and failure scenarios."

    system_instruction += "\n\nCurrent conversation:\n{history}\nCandidate: {input}\nInterviewer:"

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=system_instruction
    )
    return prompt
