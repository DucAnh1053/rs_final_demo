import numpy as np
from tqdm import tqdm
from collections import defaultdict

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

kc_names = {
    "56": "Data Model",
    "12": "Subset",
    "24": "CREATE TABLE",
    "33": "Join",
    "14": "Relational data model",
    "15": "Domain",
    "19": "Foreign key",
    "13": "Tuple",
    "17": "Relation",
    "20": "Schema",
    "7": "Cardinality",
    "23": "Data type",
    "29": "SELECT",
    "30": "INSERT",
    "31": "DELETE",
    "32": "Query",
    "35": "SELECT DISTINCT",
    "37": "COUNT",
    "38": "MIN",
    "39": "HAVING",
    "47": "Relationship",
    "27": "Candidate key",
    "34": "Primary Key",
    "55": "Superclass",
    "60": "One-To-Many",
    "6": "Cartesian product",
    "42": "Natural Join",
    "65": "Trivial",
    "51": "weak entity ",
    "61": "One-To-One",
    "48": "Entity",
    "16": "Attribute",
    "57": "Cardinality ratios",
    "50": "Data integrity",
    "11": "Difference",
    "25": "DROP TABLE",
    "45": "Entity-Relationship Model",
    "8": "Equality",
    "64": "Functional dependencies",
    "41": "Inner Join",
    "36": "GROUP BY",
    "10": "Intersection",
    "52": "Key attributes",
    "59": "Many-To-Many",
    "9": "union",
    "49": "Total ",
    "63": "partial",
    "18": "Superkey",
    "4": "Set",
    "67": "Implied",
    "69": "Minimal Cover",
    "70": "Prime Attribute",
    "76": "Relational Algebra",
    "77": "Projection",
    "85": "SQL Injection",
    "86": "REVOKE",
    "87": "Specifying Privileges - Views",
    "97": "Logging",
    "72": "Lossless Join",
    "101": "Read Uncommitted",
    "22": "DDL",
    "81": "Access Control",
    "92": "ACID Properties",
    "26": "ALTER TABLE",
    "89": "Authentication",
    "74": "Boyce-Codd normal form (BCNF)",
    "66": "Closure",
    "95": "Concurrent Transactions",
    "80": "Database Security",
    "46": "Data structure",
    "73": "Dependency preservation",
    "82": "Discretionary access control (DAC)",
    "28": "DML",
    "53": "Enhanced Entity-Relationship",
    "83": "GRANT",
    "93": "Isolation",
    "84": "Mandatory Access Control (MAC)",
    "90": "Trojan Horse attacks",
    "75": "Third normal form (3NF)",
    "99": "The Unrepeatable Read Problem",
    "100": "The Lost Update Problem",
    "102": "Read Committed",
    "91": "Transactions",
    "79": "Renaming",
    "98": "The Dirty Read Problem",
    "103": "Serializable",
    "68": "Equivalent",
    "40": "EXCEPT",
    "44": "EXISTS",
    "43": "Left Join",
    "94": "Locking",
    "96": "Two-Phase Locking (2PL) Protocol",
    "71": "Normalisation",
    "58": "Participation constraints",
    "88": "Role-Based Access Control (RBAC)",
    "78": "Selection",
    "21": "SQL",
    "54": "Subclass",
}