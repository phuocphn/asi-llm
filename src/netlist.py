from calc1 import merge_cm_transistor_cluster
from src.extract_circuit_info import (
    get_hl1_cluster_labels,
    get_hl2_cluster_labels,
    get_hl3_cluster_labels,
)
from mask_net import get_masked_netlist


class SPICENetlist:
    def __init__(self, netlist_path):
        self.netlist = get_masked_netlist(netlist_path, use_meaninful_token=True)
        self.hl1_gt = get_hl1_cluster_labels(netlist_path)
        self.hl2_gt = merge_cm_transistor_cluster(get_hl2_cluster_labels(netlist_path))
        self.hl3_gt = get_hl3_cluster_labels(netlist_path)
