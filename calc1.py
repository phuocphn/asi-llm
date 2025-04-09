from collections import defaultdict
import itertools
import json 


from loguru import logger
import sys
import datetime
log_level = "INFO"
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logfile = f"logs/{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.txt"
logger.remove() #Why does it logs duplicated message? · Issue #208 · Delgan/loguru https://github.com/Delgan/loguru/issues/208
logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
# logger.add(logfile, level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)


def assign_cluster_ids(subcircuits):
    """Assign unique cluster IDs to subcircuits and return a transistor-cluster mapping."""
    transistor_to_cluster = {}
    cluster_id = 0
    for subcircuit in subcircuits:
        for transistor in subcircuit['transistor_names']:
            if transistor.lower() not in transistor_to_cluster:
                transistor_to_cluster[transistor.lower()] =  {'cluster_names': [subcircuit['sub_circuit_name']], 'cluster_ids': [cluster_id]}  #([subcircuit['sub_circuit_name']], cluster_id)
            else:
                new_cluster_names = list(set(transistor_to_cluster[transistor.lower()]['cluster_names'] + [subcircuit['sub_circuit_name']]))
                new_cluster_ids = list(set(transistor_to_cluster[transistor.lower()]['cluster_ids'] + [cluster_id]))
                transistor_to_cluster[transistor.lower()] =  {'cluster_names': new_cluster_names, 'cluster_ids':   new_cluster_ids}# = (new_cluster, cluster_id)

        cluster_id += 1
    return transistor_to_cluster

def print_json_content(data):
    for k in data.keys():
        print (f"{k}: {data[k]}")

def get_cluster_id_transistor_mapping(mapping):
    cluster_map = defaultdict(list)
    for t, cluster_info in mapping.items():
        for cluster_id in cluster_info['cluster_ids']:
            cluster_map[cluster_id].append(t)
    return cluster_map

def filter_invalid_subcircuits(data):
    """Filter out invalid subcircuits (do not match desired keys)."""
    filtered_data = []
    for entry in data:
        if "sub_circuit_name" in entry and "transistor_names" in entry:
            filtered_data.append(entry)
    return filtered_data



def compute_cluster_metrics(predicted, ground_truth):
    """Compute correctness of transistor assignments with subcircuit type consideration."""

    # Filter out invalid subcircuits
    predicted = filter_invalid_subcircuits(predicted)
    ground_truth = filter_invalid_subcircuits(ground_truth)

    # assign cluster IDs to transistors in both predicted and ground truth data
    pred_mapping = assign_cluster_ids(predicted)
    gt_mapping = assign_cluster_ids(ground_truth)

    logger.debug ("map:\n\n")

    gt_cluster_id_mapping = get_cluster_id_transistor_mapping(gt_mapping)
    pred_cluster_id_mapping = get_cluster_id_transistor_mapping(pred_mapping)
    logger.debug (f"{gt_cluster_id_mapping=}")
    logger.debug (f"{pred_cluster_id_mapping=}")

    correct_assignments =defaultdict(int)
    for t in pred_mapping:
        if t in gt_mapping:
            if pred_mapping[t]['cluster_names'][0] in gt_mapping[t]['cluster_names']:
                correct_assignments[t] = 1
    logger.debug (f"**before** pair-wise check: {correct_assignments=}")


    for _, list_transistors in pred_cluster_id_mapping.items():
        for t in list_transistors:
            for tt in reversed(list_transistors):
                if t == tt:
                    continue

                if t not in gt_mapping or tt not in gt_mapping:
                    correct_assignments[t] = 0
                    correct_assignments[tt] = 0
                    continue

                if  len(set(gt_mapping[t]['cluster_ids']) & set(gt_mapping[tt]['cluster_ids'])) == 0:
                    # logger.debug(f"{set(gt_mapping[t]['cluster_ids'])=}")
                    # logger.debug(f"{set(gt_mapping[list_transistors[i+1]]['cluster_ids'])=}")
                    correct_assignments[t] = 0
                    correct_assignments[tt] = 0

    logger.debug (f"**after** pair-wise check: {correct_assignments=}")

    num_correct_assignments = sum([c for _, c in correct_assignments.items()])

    # Precision: Fraction of correctly assigned transistors in the predicted set
    precision = num_correct_assignments / len(pred_mapping) if pred_mapping else 0

    # Recall: Fraction of correctly assigned transistors in the ground truth set
    recall = num_correct_assignments / len(gt_mapping) if gt_mapping else 0

    # F1-score: Harmonic mean of precision and recall
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {"Precision": precision, "Recall": recall, "F1-score": f1_score}


def compute_cluster_metrics_hl1(predicted, ground_truth):
    """Compute correctness of transistor assignments with subcircuit type consideration."""
    pred_mapping = assign_cluster_ids(predicted)
    gt_mapping = assign_cluster_ids(ground_truth)

 

    correct_assignments =defaultdict(int)
    for t in pred_mapping:
        if t in gt_mapping:
            correct_assignments[t] = 1


    num_correct_assignments = sum([c for _, c in correct_assignments.items()])

    # Precision: Fraction of correctly assigned transistors in the predicted set
    precision = num_correct_assignments / len(pred_mapping) if pred_mapping else 0

    # Recall: Fraction of correctly assigned transistors in the ground truth set
    recall = num_correct_assignments / len(gt_mapping) if gt_mapping else 0

    # F1-score: Harmonic mean of precision and recall
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

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

def merge_cm_transistors(ground_truth):
    parent = {}
    rank = {}
    
    # Initialize union-find structure
    for entry in ground_truth:
        if entry['sub_circuit_name'] == 'CM':
            for transistor in entry['transistor_names']:
                if transistor not in parent:
                    parent[transistor] = transistor
                    rank[transistor] = 0

    # Perform unions
    for entry in ground_truth:
        if entry['sub_circuit_name'] == 'CM':
            # t1, t2 = entry['transistor_names']
            # union(parent, rank, t1, t2)
            transistors = entry['transistor_names']
            for i in range(1, len(transistors)):
                union(parent, rank, transistors[0], transistors[i])
    
    # Group transistors by their root representative
    merged_groups = defaultdict(set)
    for transistor in parent:
        root = find(parent, transistor)
        merged_groups[root].add(transistor)
    
    # Convert sets to sorted lists for readability
    return [sorted(list(group)) for group in merged_groups.values()]

def merge_cm_transistor_cluster(ground_truth):
    new_gt= []
    for cluster in ground_truth:
        if cluster['sub_circuit_name'] != "CM":
            new_gt.append(cluster)
    
    merged_cm_clusters = merge_cm_transistors(ground_truth)
    for cm in merged_cm_clusters:
        new_gt.append({'sub_circuit_name': 'CM', 'transistor_names': cm})
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
        "Average Recall": total_recall / n,
        "Average Precision": total_precision / n,
        "Average F1-score": total_f1 / n
    }


if __name__ == "__main__":

    # Example Data
    predicted = [
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m17', 'm18']},
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m14', 'm15']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m2', 'm3']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m7', 'm9']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m19', 'm20']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m22', 'm23']}
    ]

    ground_truth = [
        # note that `m21`, `m24` are part of current mirror (CM), but also as loads of Inverters.
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m21', 'm19', 'm20']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m24', 'm22', 'm23']},
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m17', 'm18']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm7']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm9']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm16']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm21']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm24']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm2']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m28', 'm3']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m5', 'm14']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m5', 'm15']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m25', 'm1']}
    ]

    ground_truth = merge_cm_transistor_cluster(ground_truth)


    metrics = compute_cluster_metrics(predicted, ground_truth)
    print(metrics)
