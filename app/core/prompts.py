from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import ChatPromptTemplate

class Prompts:
    class Extraction:
        EDUCATIONAL_METADATA_TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "Role: You are an Expert Curriculum Designer and Content Classifier.\n"
                "Task: Analyze the provided educational text and external search context to classify the document.\n\n"
                "Extraction Guidelines:\n"
                "- Subject: classify as Math, Science, chemistry, Physics, biology, Social science. Any other subject name."
                "- category: Strictly classify as STEM, Humanities, Arts, Language, Physical Education, or General.\n"
                "- difficulty: Strictly evaluate as Beginner, Intermediate, or Advanced based on the text's depth.\n"
                "- grade: Infer the text belongs from which class (e.g. class 10, class 12, university) .\n"
                "- chapter vs topic: 'chapter' should be the broad curriculum unit, while 'topic' is the specific lesson focus.\n"
                # "- If any metadata is ambiguous, use the search results context to make an educated pedagogical inference."
            )),
            ("human", (
                # "External Context (Search Results):\n"
                # "<context>\n{search_results}\n</context>\n\n"
                "Educational Text to Analyze:\n"
                "<document>\n{text_content}\n</document>"
            ))
        ])

        KNOWLEDGE_EXTRACTION_TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "Role: You are a Master Teacher and Pedagogical Expert.\n"
                "Task: Extract the core educational components from the source document.\n"
                "Context: This material is intended for {grade} students at a {difficulty} level studying {subject}.\n\n"
                "Pedagogical Guidelines for Extraction:\n"
                "1. learning_objectives: Must be actionable and measurable. Use Bloom's Taxonomy verbs (e.g., 'Students will be able to analyze...').\n"
                "2. definitions: Ensure the language and complexity of the definitions are strictly tailored to the {grade} level. Do not use overly academic jargon for beginners.\n"
                "3. prerequisites: What foundational knowledge is strictly required to understand this text? (You may infer this pedagogically).\n"
                "4. misconceptions: Identify 2-3 common traps or misunderstandings students at this {grade} level typically face regarding these concepts.\n"
                "5. formulae: Extract any mathematical, logical, or scientific formulas exactly as written."
            )),
            ("human", (
                "Extract the knowledge components from the following text:\n"
                "<document>\n{text}\n</document>"
            ))
        ])
        
    class Assessment:
        TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert assessment creator.\n"
                "Always generate output in JSON matching the specified format."
            )),
            ("human", "Topic: {topic}\nDifficulty: {difficulty}\nQuestion Count: {num_questions}")
        ])