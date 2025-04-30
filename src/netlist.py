from calc1 import merge_cm_transistor_cluster
from src.extract_circuit_info import (
    get_hl1_cluster_labels,
    get_hl2_cluster_labels,
    get_hl3_cluster_labels,
)
from mask_net import get_masked_netlist
from collections import defaultdict
from typing import Dict, Tuple, List


class SPICENetlist:
    def __init__(self, netlist_path):
        self.netlist = get_masked_netlist(netlist_path, use_meaninful_token=True)
        self.hl1_gt = get_hl1_cluster_labels(netlist_path)
        self.hl2_gt = merge_cm_transistor_cluster(get_hl2_cluster_labels(netlist_path))
        self.hl3_gt = get_hl3_cluster_labels(netlist_path)

    @property
    def get_graph_labels(self) -> Dict[str, Tuple[List, List, List]]:
        labels = defaultdict(list)
        subcircuit_name_to_label_ids_mapping = {
            "MosfetDiode": 1,
            "load_cap": 2,
            "compensation_cap": 3,
            "DiffPair": 1,
            "CM": 2,
            "Inverter": 3,
            "firstStage": 1,
            "secondStage": 2,
            "thirdStage": 3,
            "loadPart": 4,
            "biasPart": 5,
            "feedBack": 6,
        }
        for component in self.netlist.strip().split("\n"):
            infos = component.split(" ")
            component_name = infos[0]

            # get label for HL1
            hl1_labels = []
            for subcircuit_name, subcircuit_components in self.hl1_gt:
                if component_name in subcircuit_components:
                    hl1_labels += [
                        subcircuit_name_to_label_ids_mapping[subcircuit_name]
                    ]
            labels[component_name].append(hl1_labels)

            # get label for HL2
            hl2_labels = []
            for subcircuit_name, subcircuit_components in self.hl2_gt:
                if component_name in subcircuit_components:
                    hl2_labels += [
                        subcircuit_name_to_label_ids_mapping[subcircuit_name]
                    ]
            labels[component_name].append(hl2_labels)

            # get label for HL3
            hl3_labels = []
            for subcircuit_name, subcircuit_components in self.hl3_gt:
                if component_name in subcircuit_components:
                    hl3_labels += [
                        subcircuit_name_to_label_ids_mapping[subcircuit_name]
                    ]
            labels[component_name].append(hl3_labels)

        return labels
