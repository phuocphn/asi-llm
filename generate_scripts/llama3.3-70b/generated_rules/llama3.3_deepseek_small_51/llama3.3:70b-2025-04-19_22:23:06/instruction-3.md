
### Step 1: Identify MOSFETs with Shared Gates
Identify all MOSFETs in the SPICE netlist that share the same gate connection. This is a key characteristic of current mirrors, as they typically consist of multiple transistors with their gates tied together.

### Step 2: Determine Drain and Source Connections
For each group of MOSFETs identified in Step 1, examine their drain and source connections. In a current mirror, one transistor's drain is usually connected to a supply voltage or another node that sets the current, while the other transistors have their drains connected to replicate this current.

### Step 3: Look for Matching Transistor Pairs
Within each group of MOSFETs with shared gates, look for pairs where one transistor is NMOS and the other is PMOS, or vice versa. These complementary pairs are often used in current mirrors to create a push-pull action that helps in mirroring the current accurately.

### Step 4: Check for Current Setting Transistors
Identify transistors within each group that have their sources connected directly to the ground or to a supply voltage. These transistors typically set the reference current for the mirror.

### Step 5: Verify Replication of Current
For each potential current mirror identified, verify that the drain currents of the transistors are intended to be replicated or mirrored. This can involve tracing connections to other parts of the circuit and ensuring that the replicated currents are used appropriately (e.g., in amplifiers, buffers, or as part of a larger analog circuit).

### Step 6: Compile List of Current Mirrors
After applying the above steps, compile a list of transistor groups that fulfill all criteria for being current mirrors. Each group should include at least two transistors with shared gates and appropriate drain and source connections to replicate current.

