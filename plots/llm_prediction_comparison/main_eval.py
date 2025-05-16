from src.netlist import SPICENetlist
import glob
import json
from calc1 import compute_cluster_metrics, average_metrics
from examples.measure_fn2 import (
    evaluate_graph_clustering_node_wise,
    evaluate_graph_clustering_class_wise,
    create_confusion_matrix,
    aggregate_confusion_matrices,
)
from typing import List, Any

from typing import List, Tuple, Dict, Set


import re
from collections import defaultdict, deque


from collections import defaultdict, Counter
from typing import List
import re
import itertools
from typing import List


import plots.method_comp.evaluation_deepseek as deepseek
import plots.method_comp.evaluation_gpt as gpt
import plots.method_comp.evaluation_grok as grok
import plots.method_comp.evaluation_llama as llama


for i in range(1, 49):
    data = SPICENetlist(f"data/asi-fuboco-test/medium/{i}/")

    print(f"================================={i=}==============================")

    hl1_info, hl2_info, hl3_info = deepseek.prediction(data)
    print("-------------------")
    print("DeepSeek")
    print(hl1_info)
    print(hl2_info)
    print(hl3_info)

    hl1_info, hl2_info, hl3_info = gpt.prediction(data)
    print("-------------------")
    print("gpt")
    print(hl1_info)
    print(hl2_info)
    print(hl3_info)

    hl1_info, hl2_info, hl3_info = grok.prediction(data)
    print("-------------------")
    print("grok")
    print(hl1_info)
    print(hl2_info)
    print(hl3_info)

    hl1_info, hl2_info, hl3_info = llama.prediction(data)
    print("-------------------")
    print("llama")
    print(hl1_info)
    print(hl2_info)
    print(hl3_info)
