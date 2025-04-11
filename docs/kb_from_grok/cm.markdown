# Current Mirror Identification in SPICE Netlists

## Definition
A current mirror copies a reference current to one or more outputs. A **simple current mirror** uses transistors of the same type sharing a gate, with the reference transistor’s gate tied to its drain. A **cascoded current mirror** adds a second layer of transistors in series per branch, improving output impedance and accuracy.

## Connection Rules
1. **Same Transistor Type**: All transistors must be NMOS or PMOS.
2. **Shared Gate Connection**: 
   - Simple: All share the same gate; reference gate tied to drain.
   - Cascoded: Bottom layer shares one gate (reference tied to drain), top layer shares another gate.
3. **Reference Branch**: 
   - Simple: One transistor with gate tied to drain.
   - Cascoded: Two transistors in series; bottom gate tied to drain, top gate often tied to its drain or bias.
4. **Mirrored Branches**: 
   - Simple: Other transistors output current at drains.
   - Cascoded: Pairs of transistors in series mirror the current.
5. **Source Connection**: 
   - NMOS: Sources to ground.
   - PMOS: Sources to supply or intermediate nodes.

## Step-by-Step Procedure
1. **Parse the Netlist**: Extract transistor definitions (type, drain, gate, source, bulk).
2. **Identify Reference Transistors**: Find transistors with gate tied to drain.
3. **Group by Gate Connection**: 
   - Simple: Find same-type transistors sharing the reference gate.
   - Cascoded: Identify series pairs sharing gate connections (bottom and top layers).
4. **Check Source Connections**: 
   - NMOS: Sources to ground.
   - PMOS: Sources to supply or intermediate nodes.
5. **Verify Mirrored Branches**: 
   - Simple: Drains are outputs.
   - Cascoded: Top transistor drains are outputs; bottom connects to top’s source.
6. **Classify the Mirror**: 
   - One layer: Simple.
   - Two layers: Cascoded.
7. **Output the Mirror**: List transistors and type.