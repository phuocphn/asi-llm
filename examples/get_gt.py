from src.netlist import SPICENetlist
import glob 



data = SPICENetlist(f"data/benchmark-asi-100/small/1/")

print ("netlist:", data.netlist)
print ("hl1_gt:", data.hl1_gt)  
print ("hl2_gt:", data.hl2_gt)  


