from langchain_core.prompts import ChatPromptTemplate

class Prompts:
    class Extraction:
        EDUCATIONAL_METADATA_TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert curriculum designer."
                "Analyze the following educational text and classify its domain, target audience, and difficulty level."
            )),
            ("human", "Classify the following text:\n\nText: {text_content}")
        ])
        
        KNOWLEDGE_EXTRACTION_TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert teacher preparing a lesson plan. Extract the core educational components "
                "from the text. Keep the target audience in mind: {grade} students at a {difficulty} level "
                "studying {subject}."
            )),
            ("human", "{text}")
        ])

    class Assessment:
        TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert assessment creator.\n"
                "Always generate output in JSON matching the specified format."
            )),
            ("human", "Topic: {topic}\nDifficulty: {difficulty}\nQuestion Count: {num_questions}")
        ])