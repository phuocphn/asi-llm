import sys
import datetime
import pprint

from loguru import logger

from collections import defaultdict
from utils import configure_logging

configure_logging(level="INFO")


def assign_cluster_ids(subcircuits: list[(str, list)]):
    """Assign unique cluster IDs to subcircuits and return a transistor-cluster mapping."""
    transistor_to_cluster = {}
    cluster_id = 0
    for subcircuit_name, components in subcircuits:
        for transistor in components:
            t = transistor.lower()
            # Check if the transistor is already in the mapping
            if t not in transistor_to_cluster:
                transistor_to_cluster[t] = {
                    "cluster_names": [subcircuit_name],
                    "cluster_ids": [cluster_id],
                }
                logger.debug(
                    f"Assigning new cluster ID {cluster_id} to transistor {t} in subcircuit {subcircuit_name}"
                )
            # If the transistor is already in the mapping, update its cluster information
            else:
                current_data = transistor_to_cluster[t]
                transistor_to_cluster[t] = {
                    "cluster_names": current_data["cluster_names"] + [subcircuit_name],
                    "cluster_ids": current_data["cluster_ids"] + [cluster_id],
                }
                logger.debug(
                    f"Updating transistor {t} with new cluster ID {cluster_id} in subcircuit {subcircuit_name}"
                )

        cluster_id += 1
    return transistor_to_cluster


def print_json_content(data):
    for k in data.keys():
        print(f"{k}: {data[k]}")


def get_cluster_id_transistor_mapping(mapping):
    cluster_map = defaultdict(list)
    for t, cluster_info in mapping.items():
        for cluster_name, cluster_id in zip(
            cluster_info["cluster_names"], cluster_info["cluster_ids"]
        ):
            cluster_map[cluster_name + "-" + str(cluster_id)].append(t)
    return cluster_map


def compute_cluster_metrics(predicted, ground_truth):
    """Compute correctness of transistor assignments with subcircuit type consideration."""

    # assign cluster IDs to transistors in both predicted and ground truth data
    pred_mapping = assign_cluster_ids(predicted)
    gt_mapping = assign_cluster_ids(ground_truth)

    logger.debug(f"pred_mapping :\n\n {pred_mapping}")
    logger.debug(f"gt_mapping :\n\n {gt_mapping}")

    gt_cluster_id_mapping = get_cluster_id_transistor_mapping(gt_mapping)
    pred_cluster_id_mapping = get_cluster_id_transistor_mapping(pred_mapping)
    logger.debug("gt_cluster_id_mapping:")
    logger.debug(pprint.pformat(gt_cluster_id_mapping, indent=4))
    logger.debug("pred_cluster_id_mapping:")
    logger.debug(pprint.pformat(pred_cluster_id_mapping, indent=4))

    # Example output (for illustration):
    # { 'Inverter-0': ['m3', 'm4', 'm7', 'm5'],
    #   'CM-4': ['m3', 'm4', 'm2'],
    #   'DiffPair-2': ['m7', 'm6'],
    #   'CM-5': ['m5', 'm1', 'm11'],
    #   'Inverter-1': ['m9', 'm10', 'm8'],
    #   'CM-3': ['m9', 'm10', 'm12', 'm13']
    # }

    is_hierarchical_level1 = ground_truth[0][0] in [
        "MosfetDiode",
        "load_cap",
        "compensation_cap",
    ]

    correct_assignments = defaultdict(int)
    for t in pred_mapping:
        if t in gt_mapping:
            if is_hierarchical_level1:
                correct_assignments[t] = 1
            else:
                if (
                    pred_mapping[t]["cluster_names"][0]
                    in gt_mapping[t]["cluster_names"]
                ):
                    correct_assignments[t] = 1

    if not is_hierarchical_level1:
        logger.debug("--------------------")
        logger.debug(f"**before** pair-wise check: {correct_assignments=}")
        logger.debug("--------------------")

        for cluster_iid, list_transistors in pred_cluster_id_mapping.items():
            for t1 in list_transistors:
                for t2 in reversed(list_transistors):
                    if t1 == t2:
                        continue

                    if t1 not in gt_mapping or t2 not in gt_mapping:
                        correct_assignments[t1] = 0
                        correct_assignments[t2] = 0
                        continue

                    # If the cluster names and IDs match, mark them as correct
                    gt_overlap_cluster = set(
                        set(
                            [
                                name + "-" + str(cluster_id)
                                for name, cluster_id in zip(
                                    gt_mapping[t1]["cluster_names"],
                                    gt_mapping[t1]["cluster_ids"],
                                )
                            ]
                        )
                        & set(
                            [
                                name + "-" + str(cluster_id)
                                for name, cluster_id in zip(
                                    gt_mapping[t2]["cluster_names"],
                                    gt_mapping[t2]["cluster_ids"],
                                )
                            ]
                        )
                    )
                    logger.debug(
                        f"**`{cluster_iid}`, pair-wise check**: {t1=}, {t2=}, {gt_overlap_cluster=}"
                    )

                    if len(gt_overlap_cluster) == 0:
                        correct_assignments[t1] = 0
                        correct_assignments[t2] = 0

                    is_same_cluster = False
                    for cluster in gt_overlap_cluster:
                        if (
                            cluster[: cluster.find("-")]
                            == cluster_iid[: cluster_iid.find("-")]
                        ):
                            is_same_cluster = True
                            break
                    if not is_same_cluster:
                        correct_assignments[t1] = 0
                        correct_assignments[t2] = 0

        logger.debug("--------------------")
        logger.debug(f"**after** pair-wise check: {correct_assignments=}")
        logger.debug("--------------------")

    num_correct_assignments = sum([c for _, c in correct_assignments.items()])

    # Precision: Fraction of correctly assigned transistors in the predicted set
    precision = num_correct_assignments / len(pred_mapping) if pred_mapping else 0

    # Recall: Fraction of correctly assigned transistors in the ground truth set
    recall = num_correct_assignments / len(gt_mapping) if gt_mapping else 0

    # F1-score: Harmonic mean of precision and recall
    f1_score = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {"Precision": precision, "Recall": recall, "F1-score": f1_score}


def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])  # Path compression
    return parent[x]


def union(parent, rank, x, y):
    root_x = find(parent, x)
    root_y = find(parent, y)
    if root_x != root_y:
        if rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        elif rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        else:
            parent[root_y] = root_x
            rank[root_x] += 1


def merge_cm_transistors(ground_truth: list[(str, list)]):
    parent = {}
    rank = {}

    # Initialize union-find structure
    for subcircuit_name, components in ground_truth:
        if subcircuit_name == "CM":
            for transistor in components:
                if transistor not in parent:
                    parent[transistor] = transistor
                    rank[transistor] = 0

    # Perform unions
    for subcircuit_name, components in ground_truth:
        if subcircuit_name == "CM":
            # t1, t2 = entry['transistor_names']
            # union(parent, rank, t1, t2)
            transistors = components
            for i in range(1, len(transistors)):
                union(parent, rank, transistors[0], transistors[i])

    # Group transistors by their root representative
    merged_groups = defaultdict(set)
    for transistor in parent:
        root = find(parent, transistor)
        merged_groups[root].add(transistor)

    # Convert sets to sorted lists for readability
    return [sorted(list(group)) for group in merged_groups.values()]


def merge_cm_transistor_cluster(ground_truth: list[(str, list)]):
    new_gt = []
    for subcircuit_name, components in ground_truth:
        if subcircuit_name != "CM":
            new_gt.append((subcircuit_name, components))

    merged_cm_clusters = merge_cm_transistors(ground_truth)
    for cm in merged_cm_clusters:
        new_gt.append(("CM", cm))
    return new_gt


def average_metrics(metrics_list):
    """
    Computes the average of Precision, Recall, and F1-score from a list of metric dictionaries.

    :param metrics_list: List of dictionaries containing 'ace', 'precision', and 'f1-score'
    :return: Dictionary with averaged values
    """
    if not metrics_list:
        return {"Average Recall": 0, "Average Precision": 0, "Average F1-score": 0}

    total_recall = sum(m["Recall"] for m in metrics_list)
    total_precision = sum(m["Precision"] for m in metrics_list)
    total_f1 = sum(m["F1-score"] for m in metrics_list)

    n = len(metrics_list)

    return {
        "Average Precision": total_precision / n,
        "Average Recall": total_recall / n,
        "Average F1-score": total_f1 / n,
    }


if __name__ == "__main__":

    # Example Data
    predicted = [
        ("DiffPair", ["m17", "m18"]),
    ]
    ground_truth = [
        ("DiffPair", ["m17", "m18"]),
        ("DiffPair", ["m14", "m15"]),
        ("CM", ["m2", "m4"]),
        ("CM", ["m7", "m9"]),
        ("Inverter", ["m19", "m20"]),
        ("Inverter", ["m22", "m23"]),
    ]
    ground_truth = merge_cm_transistor_cluster(ground_truth)
    metrics = compute_cluster_metrics(predicted, ground_truth)
    print(metrics)
