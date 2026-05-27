QUESTION_BANK = {
    "langchain": {
        "ideal_answer": "LangChain is an orchestration framework for developing applications powered by language models. It provides components like chains, memory, agents, and prompt templates to build complex workflows.",
        "expected_keywords": ["chain", "memory", "prompt template", "output parser", "agent", "framework"]
    },
    "python": {
        "ideal_answer": "Python is a high-level, dynamically typed programming language known for its readability and versatility. It supports multiple programming paradigms including object-oriented and functional programming.",
        "expected_keywords": ["dynamically typed", "object-oriented", "interpreted", "readability"]
    },
    "react": {
        "ideal_answer": "React is a JavaScript library for building user interfaces using a component-based architecture. It uses a virtual DOM to optimize rendering performance.",
        "expected_keywords": ["component", "virtual dom", "state", "props", "hooks"]
    },
    "aws": {
        "ideal_answer": "AWS is a comprehensive cloud computing platform provided by Amazon, offering services for computing, storage, networking, and machine learning.",
        "expected_keywords": ["cloud", "ec2", "s3", "services", "infrastructure"]
    },
    "sql": {
        "ideal_answer": "SQL is a domain-specific language used for managing and querying relational databases. Key operations include SELECT, INSERT, UPDATE, DELETE, and JOINs.",
        "expected_keywords": ["relational", "database", "query", "join", "select"]
    },
    "machine learning": {
        "ideal_answer": "Machine learning is a subset of AI where models are trained on data to recognize patterns and make predictions without being explicitly programmed for the task.",
        "expected_keywords": ["training", "data", "model", "prediction", "patterns"]
    }
}

def get_ideal_answer(topic: str) -> dict:
    topic_lower = topic.lower()
    for key in QUESTION_BANK:
        if key in topic_lower:
            return QUESTION_BANK[key]
    return {
        "ideal_answer": f"A good answer about {topic} should demonstrate practical experience, theoretical understanding, and relevant use cases.",
        "expected_keywords": [topic]
    }
