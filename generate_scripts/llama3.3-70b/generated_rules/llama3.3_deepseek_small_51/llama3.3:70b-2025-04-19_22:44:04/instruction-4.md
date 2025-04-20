
### Step 1: Identify MOSFETs with Common Gate Connection
Identify all MOSFETs in the SPICE netlist that have their gates connected to the same node.

### Step 2: Determine Complementary MOSFET Pairs
For each group of MOSFETs identified in Step 1, determine if there are complementary pairs (one NMOS and one PMOS) with their sources connected to different power rails (e.g., ground for NMOS and supply voltage for PMOS).

### Step 3: Check Drain Connections for Complementary Pairs
Verify that the drains of the complementary MOSFET pairs identified in Step 2 are connected to each other, forming a common output node.

### Step 4: Identify Inverter Structures
Recognize that the combination of complementary MOSFET pairs with their gates tied together and drains connected forms an inverter structure. Each such structure corresponds to one **Inverter**.

### Step 5: Compile List of Inverters
Compile a list of all identified **Inverters**, where each inverter is represented by the names of its constituent MOSFETs.
