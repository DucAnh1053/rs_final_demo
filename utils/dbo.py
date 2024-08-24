from mongoengine import (
    Document,
    StringField,
    ListField,
    IntField,
    FloatField,
    BooleanField,
    DateTimeField,
    ObjectIdField,
)


class Question(Document):
    _id = StringField(required=True)
    answer = ListField(StringField(), required=True)
    correct_answer = StringField(required=True)
    knowledge_id = StringField(required=True)
    title = StringField(required=True)
    content = StringField(required=True)
    difficulty = IntField(required=True)
    multimedia = ObjectIdField(required=True)
    meta = {"collection": "questions"}


class Student(Document):
    _id = StringField(required=True)
    specialization = StringField(required=True)
    birth_year = IntField(required=True)
    full_name = StringField(required=True)
    email = StringField(required=True)
    specialization_name = StringField(required=True)

    meta = {"collection": "students"}


class Interaction(Document):
    _id = ObjectIdField(required=True)
    selection_change = IntField(required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    hint_used = BooleanField(required=True)
    time_span = FloatField(required=True)
    difficulty_feedback = IntField(required=True)
    trust_feedback = IntField(required=True)
    answer_status = BooleanField(required=True)
    student_id = StringField(required=True)
    question_id = StringField(required=True)

    meta = {"collection": "interactions"}
