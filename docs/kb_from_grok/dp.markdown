# Differential Pair Identification in SPICE Netlists

## Definition
A differential pair consists of two transistors of the same type (e.g., NMOS or PMOS) configured to amplify the difference between two input signals. They share a common source node connected to a current source (tail), have distinct gate inputs, and produce separate drain outputs.

## Connection Rules
1. **Same Transistor Type**: Both transistors must be NMOS or both PMOS.
2. **Shared Source Node**: The source terminals must connect to the same node.
3. **Tail Current Source**: The shared source node must connect to the drain of a tail transistor (same type), with its source tied to ground (NMOS) or supply (PMOS).
4. **Distinct Gate Inputs**: The gates must be driven by different input signals (e.g., in1, in2).
5. **Separate Drain Outputs**: The drains must connect to distinct nodes, typically loads or next stages.
6. **Symmetry**: The pair should exhibit symmetric connections to loads or mirrors for balanced operation.

## Step-by-Step Procedure
1. **Parse the Netlist**: Extract all transistor definitions (type, drain, gate, source, bulk).
2. **Group by Source Node**: Find pairs of same-type transistors with a shared source node.
3. **Check Tail Connection**: Verify the shared source connects to a tail transistor’s drain, with the tail’s source at ground (NMOS) or supply (PMOS).
4. **Verify Gate Inputs**: Confirm the gates connect to distinct nodes (inputs).
5. **Confirm Drain Outputs**: Ensure drains connect to separate nodes (outputs).
6. **Validate Symmetry**: Optionally, check if drains connect to symmetric loads (e.g., PMOS mirrors).
7. **Output the Pair**: If all criteria are met, classify as a differential pair.