
### Step 1: Identify MOSFET Transistors
Identify all MOSFET transistors in the SPICE netlist by looking for lines that start with 'm' and have a model type of either 'pmos' or 'nmos'.

### Step 2: Determine Drain, Source, and Gate Connections
For each MOSFET transistor, determine its drain, source, and gate connections. Note any shared connections among multiple transistors.

### Step 3: Find Common Gate Connections
Identify groups of MOSFET transistors that have their gates connected to the same node. This is a characteristic of current mirrors, where multiple transistors share the same gate voltage.

### Step 4: Check for Matching Transistor Types and Shared Drain or Source Connections
Within each group of transistors with common gate connections, verify that they are of the same type (either all 'pmos' or all 'nmos') and check if any of them also share a drain or source connection.

### Step 5: Verify Current Mirror Configuration
To confirm the presence of a current mirror, ensure that:
- The transistors in question have a common gate connection.
- At least two of them share a drain or source connection, or one transistor's drain is connected to the supply voltage or another node that sets the current, while the other transistors have their drains connected to nodes where the mirrored current will flow.
- The shared connection is not to ground or supply unless it's part of a larger current mirror structure involving multiple transistor types.

### Step 6: Analyze Supply and Ground Connections
Identify how the sources of the MOSFETs in each group are connected. In a current mirror, the sources are usually connected either to the supply voltage (for PMOS) or to ground (for NMOS), which helps in identifying the direction of current flow.

### Step 7: Verify Current Mirror Functionality
For each identified group, verify that the circuit functions as a current mirror by checking if the current flowing through one transistor is mirrored in the other transistors. This can involve analyzing the netlist for connections that would allow current to be set by one transistor and then replicated by others.

### Step 8: Compile List of Current Mirrors
Compile a list of all identified current mirrors, noting the specific MOSFETs involved in each mirror. This list represents all instances of current mirrors found within the SPICE netlist.
