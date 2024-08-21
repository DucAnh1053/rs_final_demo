import numpy as np


def __performance(answer_state, difficulty, difficulty_feedback, time_taken, k, mid):
    time_taken = np.where(time_taken < 0, 0, time_taken)
    difficulty_feedback = np.where(
        difficulty_feedback == 0, difficulty, difficulty_feedback
    )
    diff = time_taken - mid

    return np.where(
        diff < 0,
        (answer_state * difficulty / difficulty_feedback / (1 + np.exp(k * diff)) / 3),
        (
            answer_state
            * difficulty
            * (1 + np.exp(-k * diff))
            / difficulty_feedback
            / (1 + np.exp(-k * diff))
            / 3
        ),
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
    k1=0.1,
    k2=0.05,
    mid=60,
):
    return (
        w1
        * __performance(
            answer_state, difficulty, difficulty_feedback, time_taken, k1, mid
        )
        + w2 * __efficiency(selection_change, k2)
        + w3 * __strategy(hint_used)
    )


def map_id_ix(ids):
    id_to_ix = {}
    ix_to_id = {}
    for ix, id in enumerate(ids):
        id_to_ix[id] = ix
        ix_to_id[ix] = id
    return id_to_ix, ix_to_id

def check_random_state(random_state):
    """Validate the random state.

    Check a random seed or existing numpy rng
    and get back an initialized numpy.randon.Generator

    Parameters
    ----------
    random_state : int, None, np.random.RandomState or np.random.Generator
        The existing RandomState. If None, or an int, will be used
        to seed a new numpy RandomState.
    """
    # backwards compatibility
    if isinstance(random_state, np.random.RandomState):
        return np.random.default_rng(random_state.rand_int(2**31))

    # otherwise try to initialize a new one, and let it fail through
    # on the numpy side if it doesn't work
    return np.random.default_rng(random_state)