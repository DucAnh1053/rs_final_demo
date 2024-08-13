import pandas as pd
from utils.dba import InteractionDBA, QuestionDBA, StudentDBA

def get_interaction_dataframe():
    return pd.DataFrame([interaction.to_mongo().to_dict() for interaction in InteractionDBA.get_all_interactions()])

def get_question_dataframe():
    return pd.DataFrame([question.to_mongo().to_dict() for question in QuestionDBA.get_all_questions()])

def get_student_dataframe():
    return pd.DataFrame([student.to_mongo().to_dict() for student in StudentDBA.get_all_students()])