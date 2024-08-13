import numpy as np


def __performance(answer_state, difficulty, difficulty_feedback, time_taken, n):
    time_taken = np.where(time_taken < 0, 0, time_taken)
    difficulty_feedback = np.where(
        difficulty_feedback == 0, difficulty, difficulty_feedback
    )
    return (
        answer_state
        * difficulty
        / difficulty_feedback
        / (1 + np.emath.logn(n, 1 + time_taken))
        / 3
    )


def __efficiency(selection_change, k):
    return 1 / (1 + k * selection_change)


def __strategy(hint_used):
    return 1 - hint_used


def calculate_rating(
    answer_state,
    difficulty,
    difficulty_feedback,
    time_taken,
    selection_change,
    hint_used,
    w1=0.6,
    w2=0.2,
    w3=0.2,
    n=60,
    k=0.05,
):
    return (
        w1 * __performance(answer_state, difficulty, difficulty_feedback, time_taken, n)
        + w2 * __efficiency(selection_change, k)
        + w3 * __strategy(hint_used)
    )


def map_id_ix(ids):
    id_to_ix = {}
    ix_to_id = {}
    for ix, id in enumerate(ids):
        id_to_ix[id] = ix
        ix_to_id[ix] = id
    return id_to_ix, ix_to_id
