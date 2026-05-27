from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

def initialise_agent(prompt):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    memory = ConversationBufferMemory()
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )
    return chain

def get_next_question(chain, user_input, last_score, skills_covered, missing_skills):
    steering = ""
    if last_score is not None:
        if last_score < 5:
            steering = "Ask a follow-up on the same concept, the candidate's answer was weak."
        elif 5 <= last_score <= 7:
            steering = "Ask a follow-up clarification question."
        elif last_score > 7:
            steering = "Advance to next skill area."
            
    uncovered_missing = [s for s in missing_skills if s not in skills_covered]
    if uncovered_missing and (last_score is None or last_score > 7):
        steering += f" Steer toward this missing skill: {uncovered_missing[0]}."

    augmented_input = user_input
    if steering:
        augmented_input += f"\n[SYSTEM INSTRUCTION for next question: {steering}]"
    
    response = chain.predict(input=augmented_input)
    return response
