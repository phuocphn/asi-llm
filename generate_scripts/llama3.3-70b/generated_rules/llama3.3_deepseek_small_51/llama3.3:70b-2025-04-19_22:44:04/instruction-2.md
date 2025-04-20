
### Step 1: Identify MOSFETs in the Netlist
Identify all MOSFET instances in the netlist by looking for lines that start with 'm' followed by a unique identifier (e.g., m1, m2, etc.).

### Step 2: Determine MOSFET Types
For each MOSFET instance, determine if it is a PMOS or NMOS transistor based on its description in the netlist.

### Step 3: Find Complementary MOSFET Pairs
Look for pairs of MOSFETs where one is a PMOS and the other is an NMOS, and they share common connections (e.g., gates, drains, sources) that could form an inverter circuit.

### Step 4: Analyze Connections for Inverter Configuration
For each pair identified in Step 3, analyze their connections to determine if they are configured as an inverter:
- The gates of both MOSFETs should be connected to the input signal.
- The drains of both MOSFETs should be connected together, forming the output node.
- One MOSFET (PMOS) should have its source connected to the supply voltage, and the other (NMOS) should have its source connected to ground.

### Step 5: Identify Inverter Chains
In some cases, multiple inverters might be connected in a chain. Look for sequences of MOSFET pairs that match the inverter configuration, where the output of one inverter is connected to the input of another.

### Step 6: Compile List of Inverters
Compile a list of all identified inverter circuits based on the analysis from Steps 3 to 5. Each inverter should be represented by the identifiers of its constituent MOSFETs (e.g., ['m8', 'm6'], etc.).

