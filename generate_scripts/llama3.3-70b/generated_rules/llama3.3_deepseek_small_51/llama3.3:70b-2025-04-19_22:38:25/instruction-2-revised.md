
### Step 1: Extract Transistor Information
Extract all transistor (m*) elements from the SPICE netlist, including their node connections.

### Step 2: Identify Potential Differential Pairs
For each pair of transistors, check if they share the same current mirror or load transistor and have different input nodes. Also, note the nodes connected to their gates, drains, and sources.

### Step 3: Determine Gate and Drain/Source Connections
Verify that pairs of transistors either share the same gate connection node or have complementary drain/source connections (e.g., one connected to `in1` and the other to `in2`, or similar).

### Step 4: Filter by Transistor Type, Configuration, and Surrounding Circuitry
Among the paired transistors, check if they are of the same type (PMOS or NMOS) and if their configurations suggest a differential pair setup. This includes checking for connections that could form a differential amplifier structure. Examine the surrounding circuit elements (resistors, capacitors, other transistors) to ensure they do not disrupt the differential operation of the pair.

### Step 5: Verify Differential Pair Characteristics
For each potential pair, verify that their configurations match the characteristics of a differential pair:
- Both transistors are of the same type.
- Their gates are connected to different input nodes or they share a gate connection but have distinct drain/source connections.
- Their sources are connected to a common node or to each other through another transistor.
- Their drains are connected to different output nodes or to a common output node through other transistors.

### Step 6: Compile List of Differential Pairs
After verifying the configurations, compile a list of all identified differential pairs based on the criteria from Step 5.
