import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.optimize import linear_sum_assignment
from collections import defaultdict
from loguru import logger
from utils import configure_logging

configure_logging(logname="measure_fn2.log", level="INFO")
logger.info("Starting evaluation of graph clustering...")


def evaluate_graph_clustering_class_wise(ground_truth, prediction):
    """
    Evaluates graph node classification and clustering with overlapping classes.
    Transistors may belong to multiple clusters/classes.

    Use this function if you want to evaluate how well the model performs for each class.
    - If you want to evaluate how well the model performs for each class.
    - Example: You care about the performance of the model in identifying specific subcircuits like "Inverter" or "CM" across all nodes.

    Args:
        ground_truth: List of tuppes with the first element is subcircuit names, and component/transistor names as the second element'
        prediction: List of tuppes with the first element is subcircuit names, and component/transistor names as the second element'

    Returns:
        Dictionary with classification (node-level) and clustering (cluster-level) metrics
    """
    # Convert to sets for clustering
    gt_clusters = [(sc, set(components)) for sc, components in ground_truth]
    pred_clusters = [(sc, set(components)) for sc, components in prediction]

    # Node classification: map transistors to their set of classes
    gt_node_labels = defaultdict(set)
    for name, transistors in gt_clusters:
        for t in transistors:
            gt_node_labels[t].add(name)

    pred_node_labels = defaultdict(set)
    for name, transistors in pred_clusters:
        for t in transistors:
            pred_node_labels[t].add(name)

    logger.debug(f"Ground truth node labels: {gt_node_labels=}")
    logger.debug(f"Predicted node labels: {pred_node_labels=}")
    # Node-level classification metrics
    all_transistors = set(gt_node_labels.keys()) | set(pred_node_labels.keys())
    classes = sorted(
        set([name for name, _ in gt_clusters] + [name for name, _ in pred_clusters])
    )
    logger.debug(f"All classes: {classes=}")

    # Binary classification per class (multi-label)
    node_precision_scores = []
    node_recall_scores = []
    node_f1_scores = []

    for cls in classes:
        logger.debug(f"Evaluating class: {cls=}")
        y_true = []
        y_pred = []
        for t in all_transistors:
            y_true.append(1 if cls in gt_node_labels.get(t, set()) else 0)
            y_pred.append(1 if cls in pred_node_labels.get(t, set()) else 0)
        node_precision_scores.append(precision_score(y_true, y_pred, zero_division=0))
        node_recall_scores.append(recall_score(y_true, y_pred, zero_division=0))
        node_f1_scores.append(f1_score(y_true, y_pred, zero_division=0))

    # Average metrics across classes (macro averaging)
    logger.debug(f"Node-level precision scores: {node_precision_scores=}")
    node_precision = np.mean(node_precision_scores) if node_precision_scores else 0
    node_recall = np.mean(node_recall_scores) if node_recall_scores else 0
    node_f1 = np.mean(node_f1_scores) if node_f1_scores else 0

    # Cluster-level metrics: match clusters based on transistor overlap
    overlap_matrix = np.zeros((len(gt_clusters), len(pred_clusters)))
    for i, (_, gt_transistors) in enumerate(gt_clusters):
        for j, (_, pred_transistors) in enumerate(pred_clusters):
            overlap_matrix[i, j] = len(gt_transistors & pred_transistors)

    # Optimal cluster assignment using Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(-overlap_matrix)  # Maximize overlap
    cluster_correct = 0
    cluster_total_gt = sum(len(t) for _, t in gt_clusters)
    cluster_total_pred = sum(len(t) for _, t in pred_clusters)

    for gt_idx, pred_idx in zip(row_ind, col_ind):
        gt_name, gt_transistors = gt_clusters[gt_idx]
        pred_name, pred_transistors = pred_clusters[pred_idx]
        if gt_name == pred_name:
            cluster_correct += overlap_matrix[gt_idx, pred_idx]

    cluster_precision = (
        cluster_correct / cluster_total_pred if cluster_total_pred > 0 else 0
    )
    cluster_recall = cluster_correct / cluster_total_gt if cluster_total_gt > 0 else 0
    cluster_f1 = (
        2 * cluster_precision * cluster_recall / (cluster_precision + cluster_recall)
        if (cluster_precision + cluster_recall) > 0
        else 0
    )

    return {
        "node_precision": node_precision,
        "node_recall": node_recall,
        "node_f1": node_f1,
        "Precision": node_precision,
        "Recall": node_recall,
        "F1-score": node_f1,
        "cluster_precision": cluster_precision,
        "cluster_recall": cluster_recall,
        "cluster_f1": cluster_f1,
        "cluster_correct_transistors": int(cluster_correct),
        "cluster_total_predicted": cluster_total_pred,
        "cluster_total_actual": cluster_total_gt,
    }


def evaluate_graph_clustering_node_wise(ground_truth, prediction):
    """
    Evaluates graph node classification and clustering with overlapping classes.
    Transistors may belong to multiple clusters/classes.

    Use this function if you want to evaluate how well the model performs for each node.
        - If you want to evaluate how well the model performs for each individual node.
        - Example: You care about the accuracy of the predicted classes for each transistor, regardless of the overall class performance.

    Args:
        ground_truth: List of tuples with the first element as subcircuit names, and component/transistor names as the second element.
        prediction: List of tuples with the first element as subcircuit names, and component/transistor names as the second element.

    Returns:
        Dictionary with classification (node-level) and clustering (cluster-level) metrics.
    """
    # Convert to sets for clustering
    gt_clusters = [(sc, set(components)) for sc, components in ground_truth]
    pred_clusters = [(sc, set(components)) for sc, components in prediction]

    # Node classification: map transistors to their set of classes
    gt_node_labels = defaultdict(set)
    for name, transistors in gt_clusters:
        for t in transistors:
            gt_node_labels[t].add(name)

    pred_node_labels = defaultdict(set)
    for name, transistors in pred_clusters:
        for t in transistors:
            pred_node_labels[t].add(name)

    # Node-wise metrics
    all_transistors = set(gt_node_labels.keys()) | set(pred_node_labels.keys())
    node_precisions = []
    node_recalls = []
    node_f1s = []

    # multi-label classification
    # Calculate precision, recall, and F1 for each node
    # The aggregation is done by averaging the metrics across all nodes.
    for t in all_transistors:
        true_classes = gt_node_labels.get(t, set())
        pred_classes = pred_node_labels.get(t, set())

        # Calculate precision, recall, and F1 for the node
        true_positive = len(true_classes & pred_classes)
        logger.debug(
            f"Node {t}: true classes: {true_classes}, predicted classes: {pred_classes}, true positive: {true_positive}"
        )
        precision = true_positive / len(pred_classes) if pred_classes else 0
        recall = true_positive / len(true_classes) if true_classes else 0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        node_precisions.append(precision)
        node_recalls.append(recall)
        node_f1s.append(f1)

    # Average metrics across all nodes
    node_precision = np.mean(node_precisions) if node_precisions else 0
    node_recall = np.mean(node_recalls) if node_recalls else 0
    node_f1 = np.mean(node_f1s) if node_f1s else 0

    # Cluster-level metrics (unchanged)
    overlap_matrix = np.zeros((len(gt_clusters), len(pred_clusters)))
    for i, (_, gt_transistors) in enumerate(gt_clusters):
        for j, (_, pred_transistors) in enumerate(pred_clusters):
            overlap_matrix[i, j] = len(gt_transistors & pred_transistors)

    row_ind, col_ind = linear_sum_assignment(-overlap_matrix)  # Maximize overlap
    cluster_correct = 0
    cluster_total_gt = sum(len(t) for _, t in gt_clusters)
    cluster_total_pred = sum(len(t) for _, t in pred_clusters)

    for gt_idx, pred_idx in zip(row_ind, col_ind):
        gt_name, gt_transistors = gt_clusters[gt_idx]
        pred_name, pred_transistors = pred_clusters[pred_idx]
        if gt_name == pred_name:
            cluster_correct += overlap_matrix[gt_idx, pred_idx]

    cluster_precision = (
        cluster_correct / cluster_total_pred if cluster_total_pred > 0 else 0
    )
    cluster_recall = cluster_correct / cluster_total_gt if cluster_total_gt > 0 else 0
    cluster_f1 = (
        2 * cluster_precision * cluster_recall / (cluster_precision + cluster_recall)
        if (cluster_precision + cluster_recall) > 0
        else 0
    )

    return {
        "node_precision": node_precision,
        "node_recall": node_recall,
        "node_f1": node_f1,
        "Precision": node_precision,
        "Recall": node_recall,
        "F1-score": node_f1,
        "cluster_precision": cluster_precision,
        "cluster_recall": cluster_recall,
        "cluster_f1": cluster_f1,
        "cluster_correct_transistors": int(cluster_correct),
        "cluster_total_predicted": cluster_total_pred,
        "cluster_total_actual": cluster_total_gt,
    }


def compute_cluster_metrics_v2(predicted, ground_truth):
    return evaluate_graph_clustering_node_wise(ground_truth, predicted)


def create_confusion_matrix(ground_truth, prediction):
    """
    Creates a confusion matrix between ground truth and prediction.

    Args:
        ground_truth: List of tuples with the first element as subcircuit names, and component/transistor names as the second element.
        prediction: List of tuples with the first element as subcircuit names, and component/transistor names as the second element.

    Returns:
        A confusion matrix as a dictionary where keys are ground truth subcircuit names and values are dictionaries
        mapping predicted subcircuit names to the count of overlapping transistors.
    """
    # Convert to sets for clustering
    gt_clusters = [(sc, set(components)) for sc, components in ground_truth]
    pred_clusters = [(sc, set(components)) for sc, components in prediction]

    # Initialize confusion matrix
    confusion_matrix = defaultdict(lambda: defaultdict(int))

    # Populate confusion matrix
    for gt_name, gt_transistors in gt_clusters:
        for pred_name, pred_transistors in pred_clusters:
            overlap = len(gt_transistors & pred_transistors)
            if overlap > 0:
                confusion_matrix[gt_name][pred_name] += overlap

    return confusion_matrix


def aggregate_confusion_matrices(confusion_matrices):
    """
    Aggregates multiple confusion matrices into a single confusion matrix.

    Args:
        confusion_matrices: List of confusion matrices (dictionaries) where each confusion matrix corresponds to a netlist.

    Returns:
        An aggregated confusion matrix as a dictionary.
    """
    aggregated_matrix = defaultdict(lambda: defaultdict(int))

    for matrix in confusion_matrices:
        for gt_name, pred_dict in matrix.items():
            for pred_name, count in pred_dict.items():
                aggregated_matrix[gt_name][pred_name] += count

    return aggregated_matrix


# Example usage
if __name__ == "__main__":
    ground_truth = [
        ("Inverter", ["m3", "m4", "m7", "m5"]),
        ("Inverter", ["m9", "m10", "m8"]),
        ("DiffPair", ["m6", "m7"]),
        ("CM", ["m10", "m12", "m13", "m9"]),
        ("CM", ["m2", "m3", "m4"]),
        ("CM", ["m1", "m11", "m5"]),
    ]
    hl2_good_prediction = [
        ("DiffPair", ["m6", "m7"]),
        ("CM", ["m2", "m3", "m4"]),
        ("CM", ["m9", "m10", "m12", "m13"]),
        # ("CM", ["m3", "m7", "m4", "m2"]),
    ]
    hl2_bad_prediction = [
        ("DiffPair", ["m6", "m7"]),
        ("CM", ["m2", "m3", "m4", "m7"]),
        ("CM", ["m1", "m10", "m12", "m13"]),
        # ("CM", ["m3", "m7", "m4", "m2"]),
    ]

    results = evaluate_graph_clustering_node_wise(ground_truth, hl2_good_prediction)
    print("Evaluation Results:")
    for metric, value in results.items():
        print(
            f"{metric}: {value:.4f}"
            if isinstance(value, float)
            else f"{metric}: {value}"
        )

    prediction = [
        ("DiffPair", ["m6", "m7"]),
        ("CM", ["m2", "m3", "m4"]),
        ("CM", ["m9", "m10", "m12", "m13"]),
    ]

    confusion_matrix = create_confusion_matrix(ground_truth, prediction)
    print("Confusion Matrix:")
    for gt_name, pred_dict in confusion_matrix.items():
        print(f"{gt_name}:")
        for pred_name, count in pred_dict.items():
            print(f"  {pred_name}: {count}")

    # Example confusion matrices for multiple netlists
    confusion_matrices = [
        {
            "Inverter": {"Inverter": 4, "CM": 1},
            "DiffPair": {"DiffPair": 2},
            "CM": {"CM": 6},
        },
        {
            "Inverter": {"Inverter": 3},
            "DiffPair": {"DiffPair": 1, "CM": 1},
            "CM": {"CM": 5, "Inverter": 1},
        },
    ]

    aggregated_matrix = aggregate_confusion_matrices(confusion_matrices)
    print("Aggregated Confusion Matrix:")
    for gt_name, pred_dict in aggregated_matrix.items():
        print(f"{gt_name}:")
        for pred_name, count in pred_dict.items():
            print(f"  {pred_name}: {count}")
