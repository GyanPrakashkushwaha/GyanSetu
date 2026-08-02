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
                "Task: Extract the core educational components from the source document.\n\n"
                "Pedagogical Guidelines for Extraction:\n"
                "1. Language Constraint: You MUST output all extracted text in the exact 'language' specified in the metadata.\n"
                "2. Context Anchoring: Use the provided 'topic', 'chapter', and 'category' to resolve any ambiguities in the raw text.\n"
                "3. definitions: Ensure the complexity of definitions is strictly tailored to the provided 'grade' and 'difficulty'.\n"
                "4. learning_objectives: Must be actionable and measurable using Bloom's Taxonomy verbs.\n"
                "5. prerequisites: Infer the required foundational knowledge to understand this text.\n"
                "6. misconceptions: Identify 2-3 common traps students at this specific 'grade' level face.\n"
                "7. formulae: Extract any mathematical/scientific formulas exactly as written."
            )),
            ("human", (
                "Target Student & Document Context:\n"
                "<metadata>\n"
                "{metadata_json}\n"
                "</metadata>\n\n"
                "Extract the knowledge components from the following text:\n"
                "<document>\n{text}\n</document>"
            ))
        ])
        
    class Planning:
        TEACHING_PLANNER_TEMPLATE = ChatPromptTemplate.from_messages([
            ("system", (
                "Role: You are an Expert Curriculum Scheduler and Pedagogical Strategist.\n"
                "Task: I will provide you with a Target Student metadata object and 6 extracted educational components. Convert them into a logical, multi-period teaching plan.\n\n"
                "Pedagogical Sequencing & Pacing Guidelines:\n"
                "1. Language Constraint: You MUST write the entire teaching plan in the exact 'language' specified in the metadata.\n"
                "2. Context-Aware Pacing: Evaluate the volume of concepts AGAINST the target 'grade' and 'difficulty' from the metadata. Younger students or complex topics require slower pacing. Calculate the optimal number of 40-minute periods required without rushing.\n"
                "3. MECE Principle: You MUST ensure EVERY item provided in the categories below is assigned to a period.\n\n"
                "Data Mapping Rules (How you must route the explicitly provided data):\n"
                "- PREREQUISITES: MUST be covered in Period 1 to establish the baseline.\n"
                "- LEARNING OBJECTIVES: Distribute these logically as the 'learning_outcome' for the periods.\n"
                "- CORE CONCEPTS & KEY TERMS: Group related items together. Build from basic definitions to complex applications.\n"
                "- FORMULAE: Introduce these only AFTER the underlying concepts have been scheduled.\n"
                "- MISCONCEPTIONS: Map these directly into the specific period where the related concept is taught.\n\n"
                "Constraint: Do not generate new concepts. Only schedule what is explicitly provided."
            )),
            ("human", (
                "Target Student & Document Context:\n"
                "<metadata>\n"
                "{metadata_json}\n"
                "</metadata>\n\n"
                "Design the teaching strategy using the following extracted components:\n\n"
                "<prerequisites>\n{prerequisites}\n</prerequisites>\n\n"
                "<learning_objectives>\n{learning_objectives}\n</learning_objectives>\n\n"
                "<core_concepts>\n{concepts}\n</core_concepts>\n\n"
                "<key_terms>\n{key_terms}\n</key_terms>\n\n"
                "<formulae>\n{formulae}\n</formulae>\n\n"
                "<misconceptions>\n{misconceptions}\n</misconceptions>"
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