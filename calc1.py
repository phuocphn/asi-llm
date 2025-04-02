from collections import defaultdict
import itertools

def assign_cluster_ids(subcircuits):
    """Assign unique cluster IDs to subcircuits and return a transistor-cluster mapping."""
    transistor_to_cluster = {}
    cluster_id = 0
    for subcircuit in subcircuits:
        for transistor in subcircuit['transistor_names']:
            transistor_to_cluster[transistor.lower()] = (subcircuit['sub_circuit_name'], cluster_id)
        cluster_id += 1
    return transistor_to_cluster

def compute_cluster_metrics(predicted, ground_truth):
    """Compute correctness of transistor assignments with subcircuit type consideration."""
    pred_mapping = assign_cluster_ids(predicted)
    gt_mapping = assign_cluster_ids(ground_truth)

    # Set of correctly classified transistors (must match sub_circuit_name)
    # correct_assignments = sum(1 for t in pred_mapping if t in gt_mapping and pred_mapping[t] == gt_mapping[t])
    correct_assignments = 0
    for t in pred_mapping:
        # print (f"{t=}")
        if t in gt_mapping:
            # print (f"{pred_mapping[t]=}, {gt_mapping[t]=}")
            if pred_mapping[t][0] == gt_mapping[t][0]:
                correct_assignments += 1
                # print ("correctly classified: ", t)
    print (f"{correct_assignments=}")
    # exit()

    # Precision: Fraction of correctly assigned transistors in the predicted set
    precision = correct_assignments / len(pred_mapping) if pred_mapping else 0

    # Recall: Fraction of correctly assigned transistors in the ground truth set
    recall = correct_assignments / len(gt_mapping) if gt_mapping else 0

    # F1-score: Harmonic mean of precision and recall
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {"Precision": precision, "Recall": recall, "F1-score": f1_score}

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

if __name__ == "__main__":
    predicted = [ { "sub_circuit_name": "DiffPair", "transistor_names": ["m12", "m13"] }, { "sub_circuit_name": "CM", "transistor_names": ["m14", "m3", "m4", "m11"] }, { "sub_circuit_name": "CM", "transistor_names": ["m2", "m9", "m10"] }, { "sub_circuit_name": "Inverter", "transistor_names": ["m1", "m5"] }, { "sub_circuit_name": "Inverter", "transistor_names": ["m2", "m6"] }, { "sub_circuit_name": "Inverter", "transistor_names": ["m1", "m7"] }, { "sub_circuit_name": "Inverter", "transistor_names": ["m2", "m8"] } ]
    
    predicted = [
        {"sub_circuit_name": "CM", "transistor_names": ["m14", "m3", "m4", "m11"]},
        {"sub_circuit_name": "CM","transistor_names": ["m2", "m9", "m10"]},
        {"sub_circuit_name": "DiffPair", "transistor_names": ["m5", "m6"]},
        {"sub_circuit_name": "DiffPair","transistor_names": ["m7", "m8"]},
        {"sub_circuit_name": "DiffPair","transistor_names": ["m12", "m13"]}
    ]
    ground_truth =  [
        {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m12', 'm13']}, 
        {'sub_circuit_name': 'CM', 'transistor_names': ['m14', 'm3']}, 
        {'sub_circuit_name': 'CM', 'transistor_names': ['m14', 'm4']}, 
        {'sub_circuit_name': 'CM', 'transistor_names': ['m14', 'm11']}, 
        {'sub_circuit_name': 'CM', 'transistor_names': ['m2', 'm9']}, 
        {'sub_circuit_name': 'CM', 'transistor_names': ['m2', 'm10']}]

    metrics = compute_cluster_metrics(predicted, ground_truth)
    print(metrics)
