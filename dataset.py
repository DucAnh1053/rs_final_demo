import numpy as np
import pandas as pd
import scipy.sparse as sparse
from utils import controller
from utils.tools import calculate_rating, map_id_ix


class Dataset:
    def __init__(
        self,
        question_id_to_ix,
        ix_to_question_id,
        player_id_to_ix,
        ix_to_player_id,
        observation_players,
        observation_questions,
        observations,
    ):
        self.question_id_to_ix = question_id_to_ix
        self.ix_to_question_id = ix_to_question_id
        self.player_id_to_ix = player_id_to_ix
        self.ix_to_player_id = ix_to_player_id
        self.observation_players = observation_players
        self.observation_questions = observation_questions
        self.observations = observations

    def n_users(self):
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

    def build_sparse_with_ratings(self):
        return sparse.csr_matrix(
            (
                self.observations,
                (self.observation_players, self.observation_questions),
            )
        )
        
    def build_sparse(self):
        return sparse.csr_matrix(
            (
                np.ones_like(self.observations),
                (self.observation_players, self.observation_questions),
            )
        )

    def add_new_data(self, data):
        pass

    @classmethod
    def get_data_from_mongo(cls, player_ids=None):
        data_df = controller.get_merged_and_cleaned_data()

        player_id_to_ix, ix_to_player_id = map_id_ix(data_df["student_id"].unique())
        question_id_to_ix, ix_to_question_id = map_id_ix(
            data_df["question_id"].unique()
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
            observation_players=data_df["student_id"].map(player_id_to_ix).to_list(),
            observation_questions=data_df["question_id"]
            .map(question_id_to_ix)
            .to_list(),
            observations=ratings.tolist(),
        )
