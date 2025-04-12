# -*- coding: utf-8 -*-
from calc1 import compute_cluster_metrics
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
    {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m11', 'm12']},   # correct
    {'sub_circuit_name': 'DiffPair', 'transistor_names': ['m6', 'm8']},     # partially correct
    {'sub_circuit_name': 'CM', 'transistor_names': ['m2', 'm3', 'm4', 'm5']},  # partially correct
    {'sub_circuit_name': 'CM', 'transistor_names': ['m10', 'm11', 'm12']}, # wrong, not same cluster
    {'sub_circuit_name': 'CM', 'transistor_names': ['m21', 'm22']},     # partially correct
    {'sub_circuit_name': 'CM', 'transistor_names': ['m29', 'm30', 'm31']}, #wrong, not same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m2', 'm1']}, # wrong, not same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m3', 'm6']}, # wrong, not same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m4', 'm7']}, # wrong, not same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m5', 'm8']}, # wrong, not same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m10', 'm9']}, # wrong, not same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m11', 'm12']}, # wrong, should be DiffPair
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m15', 'm13']}, # partially correct
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m18', 'm16']}, # partially correct
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m21', 'm19']}, # wrrong, m19 is not in the ground truth
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m22', 'm20']}, # correct
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m29', 'm23']}, # wrong, not an Inverterr
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m30', 'm24']}, # wrong, not in a same cluster
    {'sub_circuit_name': 'Inverter', 'transistor_names': ['m31', 'm25']}, # wrong, not in a same cluster
]


# {'m21': 1, 'm22': 1, 'm15': 1, 'm13': 1, 'm18': 1, 'm16': 1, 'm19': 1, 'm20': 1, 
# 'm11': 0, 'm10': 0, 'm12': 0, 'm6': 0, 'm3': 0, 'm8': 0, 'm5': 0, 'm2': 0, 'm1': 0, 'm4': 0, 'm7': 0, 'm9': 0, 'm29': 0, 'm23': 0, 'm31': 0, 'm30': 0, 'm24': 0, 'm25': 0})


# 2025-04-12 20:05:00.025 | DEBUG    | calc1:compute_cluster_metrics:69 - gt_cluster_id_mapping=defaultdict(<class 'list'>, {0: ['m21', 'm22', 'm19', 'm20'], 7: ['m21', 'm22', 'm29', 'm30'], 1: ['m15', 'm13', 'm14'], 5: ['m13', 'm14', 'm24', 'm25'], 2: ['m18', 'm16', 'm17'], 6: ['m16', 'm17', 'm26', 'm27'], 3: ['m11', 'm12'], 4: ['m6', 'm7', 'm8', 'm9'], 8: ['m10', 'm2', 'm3', 'm31', 'm4', 'm5'], 9: ['m1', 'm23']})
# 2025-04-12 20:05:00.025 | DEBUG    | calc1:compute_cluster_metrics:70 - pred_cluster_id_mapping=defaultdict(<class 'list'>, {0: ['m11', 'm12'], 11: ['m11', 'm12'], 3: ['m11', 'm12', 'm10'], 1: ['m6', 'm8'], 7: ['m6', 'm3'], 9: ['m8', 'm5'], 2: ['m2', 'm3', 'm4', 'm5'], 6: ['m2', 'm1'], 8: ['m4', 'm7'], 10: ['m10', 'm9'], 4: ['m21', 'm22'], 14: ['m21', 'm19'], 15: ['m22', 'm20'], 16: ['m29', 'm23'], 5: ['m29', 'm30', 'm31'], 17: ['m30', 'm24'], 18: ['m31', 'm25'], 12: ['m15', 'm13'], 13: ['m18', 'm16']})
# 2025-04-12 20:05:00.025 | DEBUG    | calc1:compute_cluster_metrics:77 - **before** pair-wise check: correct_assignments=defaultdict(<class 'int'>, {'m21': 1, 'm22': 1, 'm15': 1, 'm13': 1, 'm18': 1, 'm16': 1, 'm19': 1, 'm20': 1})
# 2025-04-12 20:05:00.025 | DEBUG    | calc1:compute_cluster_metrics:97 - **after** pair-wise check: correct_assignments=defaultdict(<class 'int'>, {'m21': 1, 'm22': 1, 'm15': 1, 'm13': 1, 'm18': 1, 'm16': 1, 'm19': 1, 'm20': 1, 'm11': 0, 'm10': 0, 'm12': 0, 'm6': 0, 'm3': 0, 'm8': 0, 'm5': 0, 'm2': 0, 'm1': 0, 'm4': 0, 'm7': 0, 'm9': 0, 'm29': 0, 'm23': 0, 'm31': 0, 'm30': 0, 'm24': 0, 'm25': 0})
# 2025-04-12 20:05:00.025 | INFO     | __main__:identify_devices:199 - eval_results={'Precision': 0.3076923076923077, 'Recall': 0.26666666666666666, 'F1-score': 0.28571428571428575}
# 2025-04-12 20:05:00.025 | INFO     | __main__:identify_devices:200 - ------------------------------------

print (compute_cluster_metrics(prediction, ground_truth))
