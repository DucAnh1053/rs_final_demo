import numpy as np
from tqdm import tqdm
from collections import defaultdict

specialization_names = {
    "College of Arts and Social Sciences": "specialization_5",
    "College of Asia and the Pacific": "specialization_6",
    "College of Business and Economics": "specialization_7",
    "College of Engineering and Computer Science": "specialization_8",
    "College of Health and Medicine": "specialization_9",
    "College of Law": "specialization_10",
    "College of Science": "specialization_11",
    "College of University Scholars": "specialization_12",
    "Not Specified": "specialization_nan",
}


def recommend_cold_start(model, feature_ix, n=10):
    fea_emb = model.v_uf[feature_ix]
    rankings = fea_emb @ model.v_i.T

    return np.argsort(rankings)[:-n:-1]


def ranking_metrics_at_k_rankfm(
    model, x_train, y_train, x_test, y_test, K=10, show_progress=True, num_threads=1
):
    users = int(max(np.max(x_train[:, 0]), np.max(x_test[:, 0])) + 1)
    items = int(max(np.max(x_train[:, 1]), np.max(x_test[:, 1])) + 1)

    # Construct test set dictionary
    test_dict = defaultdict(set)
    for (user, item), value in zip(x_test, y_test):
        if value > 0:  # Assuming positive values mean relevant items
            test_dict[user].add(item)

    relevant, pr_div, total = 0.0, 0.0, 0.0
    mean_ap, ndcg, mean_auc = 0.0, 0.0, 0.0

    cg = 1.0 / np.log2(np.arange(2, K + 2))
    cg_sum = np.cumsum(cg)

    batch_size = 1000
    start_idx = 0

    # Users who have at least one item in the test set
    to_generate = np.array(list(test_dict.keys()), dtype="int32")

    progress = tqdm(total=len(to_generate), disable=not show_progress)

    while start_idx < len(to_generate):
        batch = to_generate[start_idx : start_idx + batch_size]
        ids = model.recommend(batch, n_items=10, filter_previous=True, cold_start="nan")
        start_idx += batch_size

        for batch_idx in range(len(batch)):
            u = batch[batch_idx]
            likes = test_dict[u]

            pr_div += min(K, len(likes))
            ap = 0.0
            hit = 0.0
            miss = 0.0
            auc = 0.0
            idcg = cg_sum[min(K, len(likes)) - 1]
            num_pos_items = len(likes)
            num_neg_items = items - num_pos_items

            for i in range(K):
                if ids.loc[u, i] in likes:
                    relevant += 1
                    hit += 1
                    ap += hit / (i + 1)
                    ndcg += cg[i] / idcg
                else:
                    miss += 1
                    auc += hit
            auc += ((hit + num_pos_items) / 2.0) * (num_neg_items - miss)
            mean_ap += ap / min(K, len(likes))
            mean_auc += auc / (num_pos_items * num_neg_items)
            total += 1

        progress.update(len(batch))

    progress.close()
    return {
        "precision": relevant / pr_div,
        "map": mean_ap / total,
        "ndcg": ndcg / total,
        "auc": mean_auc / total,
    }


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
