import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.optimize import linear_sum_assignment
from collections import defaultdict

def evaluate_graph_clustering(ground_truth, prediction):
    """
    Evaluates graph node classification and clustering with overlapping classes.
    Each dict represents a cluster, with 'sub_circuit_name' as the class of transistors in 'transistor_names'.
    Transistors may belong to multiple clusters/classes.
    
    Args:
        ground_truth: List of dicts with 'sub_circuit_name' and 'transistor_names'
        prediction: List of dicts with 'sub_circuit_name' and 'transistor_names'
    
    Returns:
        Dictionary with classification (node-level) and clustering (cluster-level) metrics
    """
    # Convert to sets for clustering
    gt_clusters = [(item['sub_circuit_name'], set(item['transistor_names'])) for item in ground_truth]
    pred_clusters = [(item['sub_circuit_name'], set(item['transistor_names'])) for item in prediction]
    
    # Node classification: map transistors to their set of classes
    gt_node_labels = defaultdict(set)
    for name, transistors in gt_clusters:
        for t in transistors:
            gt_node_labels[t].add(name)
    
    pred_node_labels = defaultdict(set)
    for name, transistors in pred_clusters:
        for t in transistors:
            pred_node_labels[t].add(name)
    
    # Node-level classification metrics
    all_transistors = set(gt_node_labels.keys()) | set(pred_node_labels.keys())
    classes = sorted(set([name for name, _ in gt_clusters] + [name for name, _ in pred_clusters]))
    
    # Binary classification per class (multi-label)
    node_precision_scores = []
    node_recall_scores = []
    node_f1_scores = []
    
    for cls in classes:
        y_true = []
        y_pred = []
        for t in all_transistors:
            y_true.append(1 if cls in gt_node_labels.get(t, set()) else 0)
            y_pred.append(1 if cls in pred_node_labels.get(t, set()) else 0)
        node_precision_scores.append(precision_score(y_true, y_pred, zero_division=0))
        node_recall_scores.append(recall_score(y_true, y_pred, zero_division=0))
        node_f1_scores.append(f1_score(y_true, y_pred, zero_division=0))
    
    # Average metrics across classes (macro averaging)
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
    
    cluster_precision = cluster_correct / cluster_total_pred if cluster_total_pred > 0 else 0
    cluster_recall = cluster_correct / cluster_total_gt if cluster_total_gt > 0 else 0
    cluster_f1 = (2 * cluster_precision * cluster_recall / (cluster_precision + cluster_recall)
                  if (cluster_precision + cluster_recall) > 0 else 0)
    
    return {
        'node_precision': node_precision,
        'node_recall': node_recall,
        'node_f1': node_f1,
        'cluster_precision': cluster_precision,
        'cluster_recall': cluster_recall,
        'cluster_f1': cluster_f1,
        'cluster_correct_transistors': int(cluster_correct),
        'cluster_total_predicted': cluster_total_pred,
        'cluster_total_actual': cluster_total_gt
    }

# Example usage
if __name__ == "__main__":
    ground_truth = [
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m21', 'm22', 'm19', 'm20']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m15', 'm13', 'm14']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m18', 'm16', 'm17']},
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m11', 'm12']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m6', 'm7', 'm8', 'm9']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m13', 'm14', 'm24', 'm25']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m16', 'm17', 'm26', 'm27']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m21', 'm22', 'm29', 'm30']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m10', 'm2', 'm3', 'm31', 'm4', 'm5']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m1', 'm23']},
    ]
    
    prediction = [
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m11', 'm12']},
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m6', 'm8']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m2', 'm3', 'm4', 'm5']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m10', 'm11', 'm12']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m21', 'm22']},
        {'sub_circuit_name': 'CM', 'transistor_names': ['m29', 'm30', 'm31']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m2', 'm1']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m3', 'm6']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m4', 'm7']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m5', 'm8']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m10', 'm9']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m11', 'm12']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m15', 'm13']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m18', 'm16']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m21', 'm19']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m22', 'm20']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m29', 'm23']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m30', 'm24']},
        {'sub_circuit_name': 'Inverter', 'transistor_names': ['m31', 'm25']},
    ]
    
    results = evaluate_graph_clustering(ground_truth, prediction)
    print("Evaluation Results:")
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}" if isinstance(value, float) else f"{metric}: {value}")