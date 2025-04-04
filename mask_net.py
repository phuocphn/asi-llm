import glob
import os
# PATH = glob.glob("data/netlist1/*.ckt")[0]

# print (PATH)

def mask_net(netlist_path, use_meaninful_token=False):
    netid = 97 if use_meaninful_token else 1
    mapping = {}
    spice_content = ""
    with open(netlist_path, "r") as f:
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
                        if use_meaninful_token:
                            new_line += "ground" + " "
                        else:
                            new_line += "gnd!" + " "

                    elif connection_info[i] == "sourcePmos":
                        if use_meaninful_token:
                            new_line += "supply" + " "
                        else:
                            new_line += "vdd!" + " "
                    elif connection_info[i] in ["nmos", "pmos", "ibias", "vref", "in1", "in2", "out", "out1", "out2"]:
                        new_line += connection_info[i] + " "
                    elif connection_info[i] not in mapping:
                        
                        mapping[connection_info[i]] = f"net{netid}" if not use_meaninful_token else chr(netid)#
                        netid += 1 
                        new_line += mapping[connection_info[i]] + " "
                    else:
                        new_line += mapping[connection_info[i]] + " "


            elif len(connection_info) == 3:
                new_line = connection_info[0] + " "
                for i in range(1, len(connection_info)):
                    if connection_info[i] in ["nmos", "pmos", "ibias", "vref", "in1", "in2", "out", "out1", "out2"]:
                        new_line += connection_info[i] + " "

                    elif connection_info[i] == "sourceNmos":
                        if use_meaninful_token:
                            new_line += "ground" + " "
                        else:
                            new_line += "gnd!" + " "

                    elif connection_info[i] == "sourcePmos":
                        if use_meaninful_token:
                            new_line += "supply" + " "
                        else:
                            new_line += "vdd!" + " "

                    elif connection_info[i] not in mapping:
                        mapping[connection_info[i]] = f"net{netid}" if not use_meaninful_token else chr(netid)#
                        netid += 1 
                        new_line += mapping[connection_info[i]] + " "
                    else:
                        new_line += mapping[connection_info[i]] + " "
            else:
                new_line = line
            
            new_line = new_line.strip()
            # print (new_line)
            spice_content += new_line + "\n"
    
    return spice_content

def get_masked_netlist(netlist_path, use_meaninful_token=True):
    PATH = glob.glob(os.path.join(netlist_path, "*.ckt"))[0]
    return mask_net(PATH, use_meaninful_token)
# mask_net(PATH, use_meaninful_token=True)

if __name__ == "__main__":
    print(get_masked_netlist("data/medium/netlist1/", True))