from src.netlist import SPICENetlist
import glob 

#hl2_subcircuit_names = {'DiffPair', 'CM', 'Inverter'}
subcircuit_names = []

def check_ground_truth_correctness():
    for dir in ["small", "medium", "large"]:
        for i in range(1, 101):
            try:
                data = SPICENetlist(f"data/benchmark-asi-100/{dir}/{i}/")
                print (f"dir={dir}, i={i}")
                print (data.hl2_gt)
                for sub_circuit in data.hl2_gt:
                    if sub_circuit['sub_circuit_name'] not in subcircuit_names:
                        subcircuit_names.append(sub_circuit['sub_circuit_name'])
                    
                    if len(sub_circuit["transistor_names"]) < 2:
                        print(f"found {len(sub_circuit['transistor_names'])} transistors in {sub_circuit['sub_circuit_name']} " +   "dir: " +  f"data/benchmark-asi-100/{dir}/{i}/")
                        exit(1)

            except Exception as e:
                print (f"error: {e}")
                continue

print("checking ground truth correctness...")
check_ground_truth_correctness()
print("non-standard names:")


subcircuit_names = list(set(subcircuit_names))
assert len(subcircuit_names) == 3, f"found {len(subcircuit_names)} subcircuit names: {subcircuit_names}"
assert "Inverter" in subcircuit_names
assert "CM" in subcircuit_names
assert "DiffPair" in subcircuit_names
print (subcircuit_names)
print("all subcircuit names are correct")


print("done")

