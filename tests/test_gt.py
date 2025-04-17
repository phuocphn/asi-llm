from src.netlist import SPICENetlist
import glob 
from utils import ppformat
from prompt_collections.hl2 import create_prompt_hl2

data = SPICENetlist(f"data/benchmark-asi-100/medium/32/")

print ("netlist:", data.netlist)
print ("hl1_gt:", ppformat(data.hl1_gt))
print ("hl2_gt:", ppformat(data.hl2_gt))


llama3_70b_predicted = [
    { "sub_circuit_name": "DiffPair", "transistor_names": [ "m2", "m4" ] }, 
    { "sub_circuit_name": "CM", "transistor_names": [ "m6", "m7", "m19", "m20" ] }, 
    { "sub_circuit_name": "Inverter", "transistor_names": [ "m10", "m12" ] } 
]


deepseek_predicted = [
    { "sub_circuit_name": "DiffPair", "transistor_names": ["m8", "m9"] }, 
    { "sub_circuit_name": "CM", "transistor_names": ["m19", "m20"] }, 
    { "sub_circuit_name": "CM", "transistor_names": ["m12", "m13", "m14", "m15"] } 
]

print ("-~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print ("llama3:70b predicted:", ppformat(llama3_70b_predicted))
print ("deepseek predicted:", ppformat(deepseek_predicted))

prompt = create_prompt_hl2().invoke({"netlist": data.netlist,}).to_string()
print ("prompt:", prompt)

from calc1 import compute_cluster_metrics

print ("compute_cluster_metrics llama3_70b_predicted:", compute_cluster_metrics(llama3_70b_predicted, data.hl2_gt))
print ("compute_cluster_metrics deepseek:", compute_cluster_metrics(deepseek_predicted, data.hl2_gt))