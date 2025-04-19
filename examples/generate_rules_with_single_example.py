# -----
# This example shows how to generate rules for a specific subcircuit using a single example.
# docs/kb_from_grok is generated using the following code.
# -----

from prompt_collections.rules import (
    create_gen_rule_prompt_per_subcircuit,
)


from src.netlist import SPICENetlist

data = SPICENetlist("data/benchmark-asi-100/medium/2")

ground_truth = [
    sc["transistor_names"] for sc in data.hl2_gt if sc["sub_circuit_name"] == "DiffPair"
]
generated_prompt = create_gen_rule_prompt_per_subcircuit(
    netlist=data.netlist, ground_truth=ground_truth, subcircuit_name="Differential Pair"
)
print(generated_prompt.invoke({}).to_string())

# -------------------------------------------------------
print("===" * 20)
ground_truth = [
    sc["transistor_names"] for sc in data.hl2_gt if sc["sub_circuit_name"] == "CM"
]
generated_prompt = create_gen_rule_prompt_per_subcircuit(
    netlist=data.netlist, ground_truth=ground_truth, subcircuit_name="Current Mirror"
)
print(generated_prompt.invoke({}).to_string())
# -------------------------------------------------------
print("===" * 20)
ground_truth = [
    sc["transistor_names"] for sc in data.hl2_gt if sc["sub_circuit_name"] == "Inverter"
]
generated_prompt = create_gen_rule_prompt_per_subcircuit(
    netlist=data.netlist, ground_truth=ground_truth, subcircuit_name="Inverter"
)
print(generated_prompt.invoke({}).to_string())
