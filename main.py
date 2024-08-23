import streamlit as st

from dataset import Dataset
from utils.dba import QuestionDBA
import implicit
import rankfm
import pickle
from utils.tools import recommend_cold_start, specialization_names, kc_names


@st.cache_data
def load_data():
    print("Loading dataset...")
    data = Dataset.load("dataset.pkl")
    user_ids = sorted(data.player_id_to_ix.keys(), key=lambda x: int(x))
    user_ids_filled = [
        user_id
        for user_id in user_ids
        if int(user_id) not in [992, 1024, 808, 522, 237, 820, 1180]
    ]  # Cold start users
    sparse_matrix, _ = data.train_test_split_sparse(random_state=42)
    player_features = list(specialization_names.keys())

    return data, user_ids_filled, sparse_matrix, player_features


@st.cache_data
def load_models():
    print("Loading models...")
    knn_model = implicit.nearest_neighbours.ItemItemRecommender.load("knn_model.npz")
    als_model = implicit.cpu.als.AlternatingLeastSquares.load("als_model.npz")
    with open("fm_model.pkl", "rb") as file:
        fm_model = pickle.load(file)

    return knn_model, als_model, fm_model


data, user_ids_filled, sparse_matrix, player_features = load_data()
knn_model, als_model, fm_model = load_models()


def get_predictions(model_name, user_id=None, cold_start=False, characteristics=None):
    if not cold_start:
        player_ix = data.get_player_ix(user_id)
        if model_name == "KNN":
            result, _ = knn_model.recommend(
                userid=player_ix,
                user_items=sparse_matrix[player_ix],
                N=10,
                filter_already_liked_items=True,
            )
        elif model_name == "ALS":
            result, _ = als_model.recommend(
                userid=player_ix,
                user_items=sparse_matrix[player_ix],
                N=10,
                filter_already_liked_items=True,
            )
        else:
            result = (
                fm_model.recommend(
                    users=[player_ix],
                    n_items=10,
                    filter_previous=True,
                    cold_start="nan",
                )
                .loc[player_ix]
                .values
            )
    else:
        feature_id = specialization_names[characteristics]
        feature_ix = data.get_player_feature_ix(feature_id)
        result = recommend_cold_start(fm_model, feature_ix, n=10)
    return [data.get_question_id(ix) for ix in result]


# Thiết lập sidebar
st.sidebar.title("Ứng dụng Đề xuất Câu hỏi")

# Chọn mô hình
model_name = st.sidebar.selectbox("Chọn mô hình", ("KNN", "ALS", "FM"))

# Nếu chọn FM, hiện tùy chọn người chơi đã có tương tác hoặc cold start
cold_start = False
user_id = None
characteristics = None
if model_name == "FM":
    player_type = st.sidebar.radio(
        "Chọn loại người chơi", ("Người chơi đã có tương tác", "Cold Start")
    )
    if player_type == "Người chơi đã có tương tác":
        user_id = st.sidebar.selectbox("Chọn ID người chơi", user_ids_filled)
    else:
        cold_start = True
        characteristics = st.sidebar.selectbox(
            "Chọn đặc điểm người chơi", player_features
        )
else:
    user_id = st.sidebar.selectbox("Chọn ID người chơi", user_ids_filled)

# Nút Predict
predict_button = st.sidebar.button("Predict")


# Phần chính
st.title("Kết quả Dự đoán")

if predict_button:
    predictions = get_predictions(model_name, user_id, cold_start, characteristics)
    questions = QuestionDBA.get_question_by_ids(predictions)

    st.session_state["predictions"] = questions
    st.session_state["show_clear"] = True

if "predictions" in st.session_state:
    for question in st.session_state["predictions"]:
        with st.expander(f"Câu hỏi {question._id}"):
            st.write(f"Độ khó: {question.difficulty}")
            st.write(f"KC: {kc_names[question.knowledge_id]}")
            st.write(question.content)
            if f"selected_answer_{question._id}" not in st.session_state:
                st.session_state[f"selected_answer_{question._id}"] = None

            st.video("https://youtu.be/dQw4w9WgXcQ?si=W6FhhgEkyn6F5akb")

            selected_answer = st.radio(
                f"Chọn câu trả lời",
                question.answer,
                key=f"answer_{question._id}",
                index=(
                    question.answer.index(
                        st.session_state[f"selected_answer_{question._id}"]
                    )
                    if st.session_state[f"selected_answer_{question._id}"]
                    else None
                ),
            )

            st.session_state[f"selected_answer_{question._id}"] = selected_answer

            if st.button("Xác nhận ", key=f"confirm_{question._id}"):
                if selected_answer == question.correct_answer:
                    st.success("Đáp án đúng!")
                else:
                    st.error("Đáp án đúng là: " + question.correct_answer)

# Nút Clear xuất hiện khi có kết quả dự đoán
if st.session_state.get("show_clear", False):
    clear_button = st.sidebar.button("Clear")
    if clear_button:
        st.session_state.pop("predictions", None)
        st.session_state["show_clear"] = False
        st.rerun()
else:
    st.write("Vui lòng nhập thông tin và nhấn Predict để xem kết quả.")