import streamlit as st

class QuizManager:
    def __init__(self, questions: list):
        self.questions = questions
        self.total_questions = len(self.questions)
        self.current_question_index = 0

    def get_question_at_index(self, index: int):
        # Ensure index is always within bounds using modulo arithmetic
        valid_index = index % self.total_questions
        return self.questions[valid_index]
    
    def next_question_index(self, direction=1):
        st.session_state['question_index'] = (st.session_state['question_index'] + direction) % self.total_questions