from src.netlist import SPICENetlist
import glob
from calc1 import compute_cluster_metrics


data = SPICENetlist(f"data/asi-fuboco-test/large/1/")
# print("Graph Labels: ", data.get_graph_labels)
print(
    "Graph Labels: \n",
    "\n".join([str(k) + ":" + str(v) for k, v in data.get_graph_labels.items()]),
)
