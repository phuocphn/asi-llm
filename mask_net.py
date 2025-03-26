import glob
PATH = glob.glob("data/netlist10/*.ckt")[0]

print (PATH)

netid = 1
mapping = {}
with open(PATH, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith(".suckt") or line.startswith(".SUBCKT") or line.startswith(".end "):
            continue
        
        connection_info = line.split()
        if len(connection_info) > 3:
            #continue
            # print (line)
            new_line = connection_info[0] + " "
            for i in range(1, len(connection_info)):
                if connection_info[i] == "sourceNmos":
                    new_line += "gnd!" + " "
                elif connection_info[i] == "sourcePmos":
                    new_line += "vdd!" + " "
                elif connection_info[i] in ["nmos", "pmos", "ibias", "vref", "in1", "in2", "out", "out1", "out2"]:
                    new_line += connection_info[i] + " "
                elif connection_info[i] not in mapping:
                    mapping[connection_info[i]] = f"net{netid}"
                    netid += 1 
                    new_line += mapping[connection_info[i]] + " "
                else:
                    new_line += mapping[connection_info[i]] + " "


        elif len(connection_info) == 3:
            new_line = connection_info[0] + " "
            for i in range(1, len(connection_info)):
                if connection_info[i] in ["nmos", "pmos", "ibias", "vref", "in1", "in2", "out", "out1", "out2"]:
                    new_line += connection_info[i] + " "
                elif connection_info[i] not in mapping:
                    mapping[connection_info[i]] = f"net{netid}"
                    netid += 1 
                    new_line += mapping[connection_info[i]] + " "
                else:
                    new_line += mapping[connection_info[i]] + " "
        else:
            new_line = line
        
        new_line = new_line.strip()
        print (new_line)