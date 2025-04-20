
### Step 1: Identify MOSFETs with Shared Gates
Identify all MOSFETs in the SPICE netlist that share the same gate connection. This can be done by parsing the netlist and grouping MOSFETs based on their gate node.

### Step 2: Determine Drain and Source Connections
For each group of MOSFETs with shared gates, determine the drain and source connections of each transistor. Identify if any of these transistors have their drains or sources connected to the same node.

### Step 3: Check for Current Mirror Configuration
A current mirror is formed when two or more MOSFETs with shared gates have their drains connected to different nodes, but their sources are connected to the same node, often through a common transistor or directly. Look for this configuration among the grouped transistors.

### Step 4: Identify Supply and Ground Connections
Identify which nodes in the netlist are connected to the supply voltage (VDD) and ground (GND). Current mirrors often involve transistors with their sources connected to either VDD or GND, depending on whether they are PMOS or NMOS.

### Step 5: Analyze Transistor Pairs
For each pair of transistors that share a gate and have one transistor's source connected to VDD (for PMOS) or GND (for NMOS), and the other's drain connected to a different node, consider them as part of a potential current mirror if their configurations match the criteria for mirroring current.

### Step 6: Verify Current Mirror Functionality
To confirm that a group of transistors functions as a current mirror, verify that the netlist does not contain any connections that would prevent the mirrored current from flowing as intended. This includes checking for any short circuits or unintended paths to ground or supply.

### Step 7: Compile List of Current Mirrors
After analyzing all transistor groups and verifying their configurations, compile a list of all identified current mirrors in the SPICE netlist.
