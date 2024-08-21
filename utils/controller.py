import os
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

import pandas as pd
from utils.dba import InteractionDBA, QuestionDBA, StudentDBA


def get_interaction_dataframe():
    return pd.DataFrame(
        [
            interaction.to_mongo().to_dict()
            for interaction in InteractionDBA.get_all_interactions()
        ]
    )


def get_question_dataframe():
    return pd.DataFrame(
        [question.to_mongo().to_dict() for question in QuestionDBA.get_all_questions()]
    )


def get_student_dataframe():
    return pd.DataFrame(
        [student.to_mongo().to_dict() for student in StudentDBA.get_all_students()]
    )


def get_merged_and_cleaned_data():
    students_df = get_student_dataframe()
    questions_df = get_question_dataframe()
    interaction_df = get_interaction_dataframe()

    # Merge dataframes
    merged_df = pd.merge(
        students_df, interaction_df, left_on="_id", right_on="student_id", how="right"
    )
    data_df = pd.merge(
        questions_df,
        merged_df,
        how="inner",
        left_on="_id",
        right_on="question_id",
    )

    del students_df, questions_df, interaction_df, merged_df

    # Drop unnecessary columns
    data_df.drop(
        columns=[
            "_id",
            "answer",
            "correct_answer",
            "title",
            "content",
            "_id_x",
            "birth_year",
            "full_name",
            "email",
            "specialization_name",
            "_id_y",
            "trust_feedback",
        ],
        inplace=True,
    )

    data_df.sort_values(by="start_time", inplace=True)
    data_df.drop_duplicates(
        subset=["student_id", "question_id"], keep="last", inplace=True
    )
    data_df.reset_index(drop=True, inplace=True)

    return data_df
