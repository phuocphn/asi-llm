
### Step 1: Identify MOSFET Transistors
Identify all MOSFET transistors in the SPICE netlist by looking for lines that start with 'm' and have a model type of either 'pmos' or 'nmos'.

### Step 2: Determine Drain, Source, and Gate Connections
For each MOSFET transistor, determine its drain, source, and gate connections. Note any shared connections among multiple transistors.

### Step 3: Find Common Gate Connections and Matching Transistor Types
Identify groups of MOSFET transistors that have their gates connected to the same node and are of the same type (either all 'pmos' or all 'nmos'). This is a characteristic of current mirrors, where multiple transistors share the same gate voltage.

### Step 4: Analyze Drain and Source Connections for Current Mirroring
Within each group of transistors with common gate connections, check if any of them also share a drain or source connection. Verify that the sources are connected either to the supply voltage (for PMOS) or to ground (for NMOS), which helps in identifying the direction of current flow.

### Step 5: Identify Current Setting Transistors and Replication
Identify transistors within each group that have their sources connected directly to the ground or to a supply voltage, setting the reference current for the mirror. Then, verify that the drain currents of the transistors are intended to be replicated or mirrored by tracing connections to other parts of the circuit.

### Step 6: Verify Current Mirror Configuration
To confirm the presence of a current mirror, ensure that:
- The transistors in question have a common gate connection.
- At least two of them share a drain or source connection, or one transistor's drain is connected to the supply voltage or another node that sets the current, while the other transistors have their drains connected to nodes where the mirrored current will flow.
- The shared connection is not to ground or supply unless it's part of a larger current mirror structure involving multiple transistor types.

### Step 7: Compile List of Current Mirrors
Compile a list of all identified current mirrors, noting the specific MOSFETs involved in each mirror. This list represents all instances of current mirrors found within the SPICE netlist.
