import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.optimize import linear_sum_assignment
from collections import defaultdict


def flatten_labels(label_node_pairs):
    return set((node, label) for label, nodes in label_node_pairs for node in nodes)


def measure_fn3(ground_truth, predicted):
    gt_set = flatten_labels(ground_truth)
    pred_set = flatten_labels(predicted)

    true_positives = gt_set & pred_set
    false_positives = pred_set - gt_set
    false_negatives = gt_set - pred_set

    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)

    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    )
    accuracy = tp / len(gt_set) if len(gt_set) > 0 else 0.0

    return {
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1,
        "accuracy": accuracy,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }
