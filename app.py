import streamlit as st
import os
import dotenv
from parser import extract_text_from_pdf, extract_resume_skills, extract_jd_requirements
from gap_analysis import compute_gap
from prompt_builder import build_system_prompt
from interview_agent import initialise_agent, get_next_question
from scorer import final_score
from question_bank import get_ideal_answer
from feedback import generate_report
from voice import transcribe, speak

dotenv.load_dotenv()

st.set_page_config(page_title="GenAI Interview Platform", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = 1
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {}
if "jd_data" not in st.session_state:
    st.session_state.jd_data = {}
if "gap_report" not in st.session_state:
    st.session_state.gap_report = {}
if "score_history" not in st.session_state:
    st.session_state.score_history = []
if "skills_covered" not in st.session_state:
    st.session_state.skills_covered = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "agent_chain" not in st.session_state:
    st.session_state.agent_chain = None
if "consecutive_high_scores" not in st.session_state:
    st.session_state.consecutive_high_scores = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "normal"
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

def go_to_page(page_num):
    st.session_state.page = page_num
    st.rerun()

# --- Page 1: Upload ---
if st.session_state.page == 1:
    st.title("Interview Platform - Setup")
    
    resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
    jd_file = st.file_uploader("Upload Job Description PDF", type=["pdf"])
    
    if st.button("Start Analysis"):
        if resume_file and jd_file:
            with st.spinner("Extracting text and analyzing skills with Gemini..."):
                res_text = extract_text_from_pdf(resume_file)
                jd_text = extract_text_from_pdf(jd_file)
                
                st.session_state.resume_data = extract_resume_skills(res_text)
                st.session_state.jd_data = extract_jd_requirements(jd_text)
                
                res_skills = st.session_state.resume_data.get("skills", [])
                jd_skills = st.session_state.jd_data.get("required_skills", [])
                
                st.session_state.gap_report = compute_gap(res_skills, jd_skills)
                go_to_page(2)
        else:
            st.error("Please upload both files.")

# --- Page 2: Gap Analysis Preview ---
elif st.session_state.page == 2:
    st.title("Gap Analysis Report")
    
    st.write(f"**Candidate Name:** {st.session_state.resume_data.get('name', 'N/A')}")
    st.write(f"**Role:** {st.session_state.jd_data.get('role', 'N/A')}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Matched Skills")
        for s in st.session_state.gap_report.get("matched", []):
            st.write(f"- ✅ {s}")
    with col2:
        st.subheader("Missing Skills")
        for s in st.session_state.gap_report.get("missing", []):
            st.write(f"- ❌ {s}")
    with col3:
        st.subheader("Bonus Skills")
        for s in st.session_state.gap_report.get("bonus", []):
            st.write(f"- ✨ {s}")
            
    if st.button("Begin Interview"):
        go_to_page(3)

# --- Page 3: Live Interview ---
elif st.session_state.page == 3:
    st.title("Live Interview Room")
    
    # Initialize Agent if not done
    if not st.session_state.interview_started:
        with st.spinner("Initializing Interviewer..."):
            prompt = build_system_prompt(
                st.session_state.gap_report, 
                st.session_state.resume_data.get('name', 'Candidate'),
                st.session_state.resume_data.get('projects', []),
                difficulty=st.session_state.difficulty
            )
            st.session_state.agent_chain = initialise_agent(prompt)
            
            # Get first question
            intro = f"Hello {st.session_state.resume_data.get('name', 'candidate')}, I'm ready to begin the interview."
            st.session_state.current_question = get_next_question(
                st.session_state.agent_chain, 
                intro, 
                None, 
                st.session_state.skills_covered, 
                st.session_state.gap_report.get("missing", [])
            )
            st.session_state.interview_started = True
            
            # Speak first question
            try:
                speak(st.session_state.current_question)
            except Exception as e:
                st.error(f"TTS Error: {e}")

    st.info(f"**Interviewer:** {st.session_state.current_question}")
    
    # Check if we should end
    total_req_skills = len(st.session_state.jd_data.get("required_skills", []))
    all_covered = total_req_skills > 0 and len(st.session_state.skills_covered) >= total_req_skills
    
    if st.session_state.question_count >= 10 or (all_covered and st.session_state.question_count > 0):
        st.success("Interview Complete!")
        if st.button("View Feedback Report"):
            go_to_page(4)
    else:
        st.write(f"Question {st.session_state.question_count + 1} of 10")
        
        # Audio Input
        audio_value = st.audio_input("Record your answer")
        
        if audio_value:
            with st.spinner("Transcribing and analyzing..."):
                # Save to temp file
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio_value.getbuffer())
                
                try:
                    answer_text = transcribe("temp_audio.wav")
                except Exception as e:
                    answer_text = f"Transcription Error: {e}"
                
                st.write(f"**You said:** {answer_text}")
                
                # Determine current skill context roughly by checking keywords in question
                current_skill = "general"
                all_skills = st.session_state.gap_report.get("matched", []) + st.session_state.gap_report.get("missing", [])
                for s in all_skills:
                    if s.lower() in st.session_state.current_question.lower():
                        current_skill = s
                        break
                        
                if current_skill not in st.session_state.skills_covered and current_skill != "general":
                    st.session_state.skills_covered.append(current_skill)
                
                # Score the answer
                ideal_data = get_ideal_answer(current_skill)
                score_res = final_score(
                    answer_text, 
                    ideal_data["ideal_answer"], 
                    ideal_data["expected_keywords"], 
                    st.session_state.current_question, 
                    ideal_data["ideal_answer"]
                )
                
                score_val = score_res["final_score"]
                st.write(f"**Score:** {score_val}/10")
                st.write(f"**Feedback:** {score_res['feedback']}")
                
                st.session_state.score_history.append({
                    "skill": current_skill,
                    "score": score_val
                })
                
                if score_val >= 8.0:
                    st.session_state.consecutive_high_scores += 1
                else:
                    st.session_state.consecutive_high_scores = 0
                    
                if st.session_state.consecutive_high_scores >= 3 and st.session_state.difficulty == "normal":
                    st.session_state.difficulty = "hard"
                    st.toast("Escalating difficulty to HARD!")
                    prompt = build_system_prompt(
                        st.session_state.gap_report, 
                        st.session_state.resume_data.get('name', 'Candidate'),
                        st.session_state.resume_data.get('projects', []),
                        difficulty="hard"
                    )
                    st.session_state.agent_chain.prompt = prompt
                
                st.session_state.question_count += 1
                
                if st.session_state.question_count < 10 and not (all_covered and st.session_state.question_count > 0):
                    # Get next question
                    st.session_state.current_question = get_next_question(
                        st.session_state.agent_chain, 
                        answer_text, 
                        score_val, 
                        st.session_state.skills_covered, 
                        st.session_state.gap_report.get("missing", [])
                    )
                    try:
                        speak(st.session_state.current_question)
                    except Exception as e:
                        st.error(f"TTS Error: {e}")
                    st.rerun()
                else:
                    st.rerun()

# --- Page 4: Feedback Report ---
elif st.session_state.page == 4:
    st.title("Final Feedback Report")
    
    with st.spinner("Generating summary..."):
        report = generate_report(st.session_state.score_history, st.session_state.skills_covered)
    
    st.metric("Overall Score", f"{report['overall_score']}/10")
    
    recom_color = "green" if "Strong" in report['recommendation'] else ("orange" if "Hire" in report['recommendation'] else "red")
    st.markdown(f"### Recommendation: <span style='color:{recom_color}'>{report['recommendation']}</span>", unsafe_allow_html=True)
    
    st.write(f"**Summary:** {report['summary']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Strengths")
        for s in report['strengths']:
            st.write(f"- ✅ {s}")
    with col2:
        st.subheader("Gaps")
        for s in report['gaps']:
            st.write(f"- ❌ {s}")
            
    st.subheader("Per-Skill Breakdown")
    for skill, score in report['per_skill_scores'].items():
        color = "green" if score > 7 else ("orange" if score >= 5 else "red")
        st.markdown(f"- {skill}: <span style='color:{color}'>{score}/10</span>", unsafe_allow_html=True)
        
    if st.button("Start New Interview"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
