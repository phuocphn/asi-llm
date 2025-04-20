
### Step 1: Identify All Transistors in the Netlist
List all transistor elements (e.g., `m1`, `m2`, etc.) present in the SPICE netlist.

### Step 2: Determine the Gate Connections of Each Transistor
For each transistor identified, note the node connected to its gate.

### Step 3: Identify Common Gate Connections
Find pairs of transistors that share the same gate connection node.

### Step 4: Filter by Transistor Type and Drain/Source Connections
Among the paired transistors with common gate connections, check if one is a PMOS transistor and the other is also a PMOS transistor, or if their drain/source connections suggest a differential configuration (i.e., they are connected in such a way that they could form a differential pair).

### Step 5: Verify Differential Pair Configuration
For each potential pair from Step 4, verify that their configurations (including gate, drain, source, and bulk connections) match the characteristics of a differential pair. Specifically, look for:
- Both transistors being of the same type (PMOS in this context).
- Their gates being connected to different input nodes (`in1` and `in2` in the example).
- Their sources being connected to a common node or to each other through another transistor.
- Their drains being connected to different output nodes or to a common output node through other transistors.

### Step 6: Compile List of Differential Pairs
After verifying the configurations, compile a list of all identified differential pairs based on the criteria from Step 5.
