
### Step 1: Identify All Transistors in the Netlist
List all transistor elements (e.g., `m1`, `m2`, etc.) present in the SPICE netlist.

### Step 2: Determine Gate and Drain/Source Connections of Each Transistor
For each identified transistor, note the nodes connected to its gate, drain, and source.

### Step 3: Identify Pairs with Common Gate or Complementary Connections
Find pairs of transistors that either share the same gate connection node or have complementary drain/source connections (e.g., one connected to `in1` and the other to `in2`, or similar).

### Step 4: Filter by Transistor Type and Configuration
Among the paired transistors, check if they are of the same type (PMOS or NMOS) and if their configurations suggest a differential pair setup. This includes checking for connections that could form a differential amplifier structure.

### Step 5: Verify Differential Pair Characteristics
For each potential pair, verify that their configurations match the characteristics of a differential pair:
- Both transistors are of the same type.
- Their gates are connected to different input nodes or they share a gate connection but have distinct drain/source connections.
- Their sources are connected to a common node or to each other through another transistor.
- Their drains are connected to different output nodes or to a common output node through other transistors.

### Step 6: Compile List of Differential Pairs
After verifying the configurations, compile a list of all identified differential pairs based on the criteria from Step 5.
