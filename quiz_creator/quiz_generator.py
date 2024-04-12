import json

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError("Vectorstore not provided.")
        # Enable a Retriever
        self.retriever = self.vectorstore.as_retriever()

        self.question_bank = [] # Initialize the question bank to store questions
        system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """
        # Use the system template to create a PromptTemplate
        self.prompt = PromptTemplate.from_template(system_template)
    
    def init_llm(self):
        self.llm = VertexAI(
            model_name = "gemini-pro",
            temperature = 0.8, # Increased for less deterministic questions 
            max_output_tokens = 500
        )

    def generate_question_with_vectorstore(self):
        # return: A JSON object representing the generated quiz question.
        
        # RunnableParallel allows Retriever to get relevant documents
        setup_and_retrieval = RunnableParallel(
            {"context": self.retriever, "topic": RunnablePassthrough()}
        )
        # Create a chain with the Retriever, PromptTemplate, and LLM
        chain = setup_and_retrieval | self.prompt | self.llm 

        # Invoke the chain with the topic as input
        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        self.question_bank = [] # Reset the question bank

        for _ in range(self.num_questions):
            question_str = self.generate_question_with_vectorstore() # Use class method to generate question
            try:
                # Convert the JSON String to a dictionary
                question = json.loads(question_str)
            except json.JSONDecodeError:
                print("Failed to decode question JSON.")
                continue 

            if self.validate_question(question):
                print("Successfully generated unique question")
                self.question_bank.append(question)
            else:
                print("Duplicate or invalid question detected.")

        return self.question_bank

    def validate_question(self, question: dict) -> bool:
        # Consider missing 'question' key as invalid in the dict object
        q = question['question']
        is_unique = True
        for d in self.question_bank:
            if d.get('question') == q:
                is_unique = False
                break
        return is_unique