import numpy as np
import pandas as pd
import scipy.sparse as sparse
from utils import controller
from utils.tools import calculate_rating, map_id_ix, check_random_state
import pickle


class Dataset:
    def __init__(
        self,
        question_id_to_ix,
        ix_to_question_id,
        player_id_to_ix,
        ix_to_player_id,
        observation_players,
        observation_questions,
        weights,
        answer_state,
        player_features=None,
        question_features=None,
    ):
        self.question_id_to_ix = question_id_to_ix
        self.ix_to_question_id = ix_to_question_id
        self.player_id_to_ix = player_id_to_ix
        self.ix_to_player_id = ix_to_player_id
        self.observation_players = observation_players
        self.observation_questions = observation_questions
        self.weights = weights
        self.answer_state = answer_state
        self.player_features = player_features
        self.question_features = question_features

    def n_players(self):
        return len(self.player_id_to_ix)

    def n_items(self):
        return len(self.question_id_to_ix)

    def get_player_id(self, ix):
        return self.ix_to_player_id[ix]

    def get_question_id(self, ix):
        return self.ix_to_question_id[ix]

    def get_player_ix(self, id):
        return self.player_id_to_ix[id]

    def get_question_ix(self, id):
        return self.question_id_to_ix[id]

    def get_numpy_weights(self):
        return np.array(self.weights)

    def build_sparse_weights(self, shape=None):
        return sparse.csr_matrix(
            (
                self.weights,
                (self.observation_players, self.observation_questions),
            ),
            shape=shape,
        )

    def get_player_question_interaction(self):
        return np.column_stack((self.observation_players, self.observation_questions))

    def train_test_split_sparse(self, train_percentage=0.8, random_state=None):
        ratings = self.build_sparse_weights().tocoo()
        random_state = check_random_state(random_state)
        random_index = random_state.random(len(ratings.data))
        train_index = random_index < train_percentage
        test_index = random_index >= train_percentage

        train = sparse.csr_matrix(
            (
                ratings.data[train_index],
                (ratings.row[train_index], ratings.col[train_index]),
            ),
            shape=ratings.shape,
            dtype=ratings.dtype,
        )

        test = sparse.csr_matrix(
            (
                ratings.data[test_index],
                (ratings.row[test_index], ratings.col[test_index]),
            ),
            shape=ratings.shape,
            dtype=ratings.dtype,
        )

        test.data[test.data < 0] = 0
        test.eliminate_zeros()

        return train, test

    def train_test_split_interaction(self, train_percentage=0.8, random_state=None):
        random_state = check_random_state(random_state)
        random_index = random_state.random(len(self.observation_players))
        train_index = random_index < train_percentage
        test_index = random_index >= train_percentage

        player_arr = np.array(self.observation_players)
        question_arr = np.array(self.observation_questions)

        x_train = np.column_stack(
            (
                player_arr[train_index],
                question_arr[train_index],
            )
        )

        y_train = np.array(self.weights)[train_index]

        x_test = np.column_stack(
            (
                player_arr[test_index],
                question_arr[test_index],
            )
        )

        y_test = np.array(self.weights)[test_index]

        return x_train, y_train, x_test, y_test

    def add_new_data(self, data):
        pass

    def save(self, path):
        with open("dataset.pkl", "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as file:
            return pickle.load(file)

    @classmethod
    def get_data_from_mongo(cls, player_ids=None):
        data_df = controller.get_merged_and_cleaned_data()

        player_id_to_ix, ix_to_player_id = map_id_ix(data_df["student_id"].unique())
        question_id_to_ix, ix_to_question_id = map_id_ix(
            data_df["question_id"].unique()
        )
        data_df["student_ix"] = data_df["student_id"].map(player_id_to_ix)
        data_df["question_ix"] = data_df["question_id"].map(question_id_to_ix)

        player_features = pd.get_dummies(
            data_df[["student_ix", "specialization"]].drop_duplicates(),
            columns=["specialization"],
            dummy_na=True,
        )
        question_features = pd.get_dummies(
            data_df[["question_ix", "knowledge_id"]].drop_duplicates(),
            columns=["knowledge_id"],
            dummy_na=True,
        )

        ratings = calculate_rating(
            data_df["answer_status"].values,
            data_df["difficulty"].values,
            data_df["difficulty_feedback"].values,
            data_df["time_span"].values,
            data_df["selection_change"].values,
            data_df["hint_used"].values,
        )

        return cls(
            question_id_to_ix=question_id_to_ix,
            ix_to_question_id=ix_to_question_id,
            player_id_to_ix=player_id_to_ix,
            ix_to_player_id=ix_to_player_id,
            observation_players=data_df["student_ix"].to_list(),
            observation_questions=data_df["question_ix"].to_list(),
            weights=ratings.tolist(),
            answer_state=data_df["answer_status"].to_list(),
            player_features=player_features.values,
            question_features=question_features.values,
        )
