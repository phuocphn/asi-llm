
### Step 1: Identify MOSFETs with Common Gate Connection
Identify all MOSFETs in the SPICE netlist that have their gates connected to a common node.

### Step 2: Determine Complementary MOSFET Pairs
For each pair of MOSFETs identified in Step 1, check if one is an nmos and the other is a pmos. This indicates a potential complementary pair.

### Step 3: Check Drain and Source Connections
Verify that the drains of the complementary MOSFET pairs are connected to the output node (out) or another internal node that eventually connects to the output, and their sources are connected to either the supply voltage or ground.

### Step 4: Identify Inverter Structures
An inverter structure consists of two complementary MOSFETs where one is an nmos with its source connected to ground and the other is a pmos with its source connected to the supply voltage. The gates of both transistors should be connected to the input node (in1, in2, etc.), and their drains should be connected to the output node or form a path to it through other transistors.

### Step 5: Group Transistors Forming Inverters
Group the MOSFETs that meet the conditions outlined in Steps 1-4 into sets. Each set represents an inverter if it contains at least one nmos and one pmos transistor with their gates connected to a common input node, and their drains contribute to forming the output.

### Step 6: Validate Inverter Functionality
For each group identified as a potential inverter, validate that the connection of the transistors indeed forms an inverting logic function. This means when the input is high, the output should be low, and vice versa, facilitated by the complementary action of the nmos and pmos transistors.

### Step 7: Compile List of Inverters
Compile a list of all transistor groups that have been validated as inverters according to the criteria outlined in Steps 1-6.
