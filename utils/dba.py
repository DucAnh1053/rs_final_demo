import os
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

from dotenv import load_dotenv
import logging
from mongoengine import (
    connect,
    disconnect,
    Document,
    NotUniqueError,
    ValidationError,
    DoesNotExist,
    OperationError,
    errors,
    get_db,
)
from pymongo.errors import WriteError, WriteConcernError
from utils.dbo import Question, Student, Interaction


# Load environment variables from the .env file
load_dotenv()

# Retrieve MongoDB credentials from environment variables
username = os.getenv("MONGODB_USERNAME")
password = os.getenv("MONGODB_PASSWORD")
database_name = os.getenv("MONGODB_DB_NAME")

# Setup logging
logging.basicConfig(filename="log/db_operations.log", level=logging.ERROR)

# Construct the MongoDB URI
uri = f"mongodb+srv://{username}:{password}@cluster0.czn0pgn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

connect(db=database_name, host=uri)
print("Connected to MongoDB")


class QuestionDBA:
    # @staticmethod
    # def create_question(data):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 question = Question(**data)
    #                 question.save()
    #                 return question
    #     except (ValidationError, NotUniqueError, WriteError, WriteConcernError) as e:
    #         logging.error(f"Error creating question: {e}")
    #         return None

    @staticmethod
    def get_question_by_id(question_id):
        try:
            question = Question.objects.get(_id=question_id)
            return question
        except DoesNotExist:
            logging.error(f"Question with id {question_id} does not exist.")
            return None
        
    @staticmethod
    def get_question_by_ids(question_ids):
        try:
            questions = Question.objects(_id__in=question_ids)
            return list(questions)  # Return as a list of Question objects
        except Exception as e:
            logging.error(f"Error retrieving questions {question_ids}: {e}")
            return None

    @staticmethod
    def get_all_questions():
        try:
            questions = Question.objects.all()
            return list(questions)  # Return as a list of Question objects
        except Exception as e:
            logging.error(f"Error retrieving all questions: {e}")
            return None

    # @staticmethod
    # def update_question(question_id, data):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 question = Question.objects.get(_id=question_id)
    #                 question.update(**data)
    #                 return question.reload()
    #     except (DoesNotExist, ValidationError, WriteError, WriteConcernError) as e:
    #         logging.error(f"Error updating question: {e}")
    #         return None

    # @staticmethod
    # def delete_question(question_id):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 question = Question.objects.get(_id=question_id)
    #                 question.delete()
    #                 return True
    #     except DoesNotExist:
    #         logging.error(f"Question with id {question_id} does not exist.")
    #         return False
    #     except (WriteError, WriteConcernError) as e:
    #         logging.error(f"Error deleting question: {e}")
    #         return False


class StudentDBA:
    # @staticmethod
    # def create_student(data):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 student = Student(**data)
    #                 student.save()
    #                 return student
    #     except (ValidationError, NotUniqueError, WriteError, WriteConcernError) as e:
    #         logging.error(f"Error creating student: {e}")
    #         return None

    @staticmethod
    def get_student_by_id(student_id):
        try:
            student = Student.objects.get(_id=student_id)
            return student
        except DoesNotExist:
            logging.error(f"Student with id {student_id} does not exist.")
            return None

    @staticmethod
    def get_all_students():
        try:
            students = Student.objects.all()
            return list(students)  # Return as a list of Student objects
        except Exception as e:
            logging.error(f"Error retrieving all students: {e}")
            return None

    # @staticmethod
    # def update_student(student_id, data):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 student = Student.objects.get(_id=student_id)
    #                 student.update(**data)
    #                 return student.reload()
    #     except (DoesNotExist, ValidationError, WriteError, WriteConcernError) as e:
    #         logging.error(f"Error updating student: {e}")
    #         return None

    # @staticmethod
    # def delete_student(student_id):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 student = Student.objects.get(_id=student_id)
    #                 student.delete()
    #                 return True
    #     except DoesNotExist:
    #         logging.error(f"Student with id {student_id} does not exist.")
    #         return False
    #     except (WriteError, WriteConcernError) as e:
    #         logging.error(f"Error deleting student: {e}")
    #         return False


class InteractionDBA:
    # @staticmethod
    # def create_interaction(data):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 interaction = Interaction(**data)
    #                 interaction.save()
    #                 return interaction
    #     except (ValidationError, NotUniqueError, WriteError, WriteConcernError) as e:
    #         logging.error(f"Error creating interaction: {e}")
    #         return None

    @staticmethod
    def get_interaction_by_id(interaction_id):
        try:
            interaction = Interaction.objects.get(_id=interaction_id)
            return interaction
        except DoesNotExist:
            logging.error(f"Interaction with id {interaction_id} does not exist.")
            return None

    @staticmethod
    def get_all_interactions():
        try:
            interactions = Interaction.objects.all()
            return list(interactions)  # Return as a list of Interaction objects
        except Exception as e:
            logging.error(f"Error retrieving all interactions: {e}")
            return None

    # @staticmethod
    # def update_interaction(interaction_id, data):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 interaction = Interaction.objects.get(_id=interaction_id)
    #                 interaction.update(**data)
    #                 return interaction.reload()
    #     except (DoesNotExist, ValidationError, WriteError, WriteConcernError) as e:
    #         logging.error(f"Error updating interaction: {e}")
    #         return None

    # @staticmethod
    # def delete_interaction(interaction_id):
    #     try:
    #         with get_db().client.start_session() as session:
    #             with session.start_transaction():
    #                 interaction = Interaction.objects.get(_id=interaction_id)
    #                 interaction.delete()
    #                 return True
    #     except DoesNotExist:
    #         logging.error(f"Interaction with id {interaction_id} does not exist.")
    #         return False
    #     except (WriteError, WriteConcernError) as e:
    #         logging.error(f"Error deleting interaction: {e}")
    #         return False
