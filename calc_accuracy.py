def evaluate_prediction(predicted, ground_truth):
    """
    Computes Precision, F1-score, and Absolute Count Error (ACE)
    for predicted and ground truth diode-connected transistors.

    :param predicted: dict with keys "number_of_diode_connected_transistors" and "transistor_names"
    :param ground_truth: dict with keys "number_of_diode_connected_transistors" and "transistor_names"
    :return: A dictionary with Precision, F1-score, and ACE
    """
    # Extract values
    pred_count = predicted["number_of_diode_connected_transistors"]
    true_count = ground_truth["number_of_diode_connected_transistors"]
    
    pred_set = set(predicted["transistor_names"])
    true_set = set(ground_truth["transistor_names"])
    
    # Compute Absolute Count Error (ACE)
    # A lower ACE value indicates better accuracy.
    ace = abs(pred_count - true_count)
    
    # Compute Precision
    intersection = len(pred_set & true_set)
    precision = intersection / len(pred_set) if pred_set else 0.0
    
    # Compute Recall
    recall = intersection / len(true_set) if true_set else 0.0
    
    # Compute F1-score
    # The closer F1-score is to 1, the better the match.
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "Precision": precision,
        "F1-score": f1_score,
        "ACE": ace
    }

def average_metrics(metrics_list):
    """
    Computes the average of ACE, Precision, and F1-score from a list of metric dictionaries.

    :param metrics_list: List of dictionaries containing 'ace', 'precision', and 'f1-score'
    :return: Dictionary with averaged values
    """
    if not metrics_list:
        return {"Average ACE": 0, "Average Precision": 0, "Average F1-score": 0}
    
    total_ace = sum(m["ACE"] for m in metrics_list)
    total_precision = sum(m["Precision"] for m in metrics_list)
    total_f1 = sum(m["F1-score"] for m in metrics_list)
    
    n = len(metrics_list)
    
    return {
        "Average ACE": total_ace / n,
        "Average Precision": total_precision / n,
        "Average F1-score": total_f1 / n
    }


def average_metrics_v2(metrics_list):
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

def test_evaluate_prediction():   
    # Example usage:
    predicted = {
        "number_of_diode_connected_transistors": 6,
        "transistor_names": ['m5', 'm12', 'm15', 'm16', 'm18', 'm19']
    }

    ground_truth = {
        "number_of_diode_connected_transistors": 7,
        "transistor_names": ['m5', 'm18', 'm19', 'm15', 'm12', 'm20', 'm16']
    }

    result = evaluate_prediction(predicted, ground_truth)
    print(result)

if __name__ == "__main__":
    #test_evaluate_HL2_predictions()
    res = [{'Precision': 0.5454545454545454, 'Recall': 0.3157894736842105, 'F1-score': 0.39999999999999997},
        {'Precision': 0.45454545454545453, 'Recall': 0.29411764705882354, 'F1-score': 0.35714285714285715},
        {'Precision': 0.5, 'Recall': 0.14285714285714285, 'F1-score': 0.22222222222222224},
        {'Precision': 0.2727272727272727, 'Recall': 0.14285714285714285, 'F1-score': 0.18749999999999997},
        {'Precision': 0.2857142857142857, 'Recall': 0.08333333333333333, 'F1-score': 0.12903225806451613},
        {'Precision': 0.5714285714285714, 'Recall': 0.34782608695652173, 'F1-score': 0.4324324324324324},
        {'Precision': 0.4166666666666667, 'Recall': 0.18518518518518517, 'F1-score': 0.2564102564102564},
        {'Precision': 0.38461538461538464, 'Recall': 0.1724137931034483, 'F1-score': 0.23809523809523808},
        {'Precision': 0.6, 'Recall': 0.1875, 'F1-score': 0.2857142857142857},
        {'Precision': 0.36363636363636365, 'Recall': 0.14814814814814814, 'F1-score': 0.21052631578947367}]
    print (average_metrics_v2(res))