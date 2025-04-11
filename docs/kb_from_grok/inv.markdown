# Analog Inverter Identification in SPICE Netlists

## Definition
An analog inverter inverts an input signal using a pull-up (PMOS) and pull-down (NMOS) structure. A **simple inverter** has one PMOS and one NMOS with shared gate (input) and drain (output). A **cascoded inverter** includes an additional NMOS in series with the pull-down NMOS, with the output at the top NMOS drain, enhancing gain or impedance.

## Connection Rules
1. **Complementary Transistors**: At least one PMOS (source to supply) and one NMOS (source to ground or intermediate node).
2. **Shared Output Node**: 
   - Simple: PMOS drain and NMOS drain connect to the same node (output).
   - Cascoded: PMOS drain connects to the top NMOS drain, with a second NMOS in series to ground.
3. **Input Node**: 
   - Simple: PMOS and NMOS gates tied together (input).
   - Cascoded: Top NMOS gate is the primary input; bottom NMOS gate may be a bias or secondary input.
4. **Series Connection (Cascoded)**: For cascoded, two NMOS transistors in series (bottom NMOS drain to top NMOS source).

## Step-by-Step Procedure
1. **Parse the Netlist**: Extract transistor definitions (type, drain, gate, source, bulk).
2. **Identify PMOS Pull-Ups**: Find PMOS transistors with source to supply.
3. **Identify NMOS Pull-Downs**: Find NMOS transistors with source to ground or an intermediate node.
4. **Check Simple Inverter**:
   - Find a PMOS-NMOS pair with:
     - Drains connected (output).
     - Gates connected (input).
   - Classify as simple inverter.
5. **Check Cascoded Inverter**:
   - Find a PMOS and two NMOS transistors where:
     - PMOS drain connects to top NMOS drain (output).
     - Top NMOS source connects to bottom NMOS drain.
     - Bottom NMOS source to ground.
     - Top NMOS gate is the input; bottom NMOS gate may differ.
   - Classify as cascoded inverter.
6. **Output the Inverter**: List transistors and type (simple or cascoded).