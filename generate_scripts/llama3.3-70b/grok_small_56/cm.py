from collections import defaultdict


class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[px] = py


def parse_netlist(lines):
    transistors = []
    for line in lines:
        if line.startswith("m"):
            tokens = line.split()
            if len(tokens) >= 6 and tokens[5] in ["pmos", "nmos"]:
                transistors.append(
                    {
                        "name": tokens[0],
                        "drain": tokens[1],
                        "gate": tokens[2],
                        "source": tokens[3],
                        "bulk": tokens[4],
                        "type": tokens[5],
                    }
                )
    return transistors


def find_current_mirrors(transistors):
    # Group transistors by gate connection
    groups = defaultdict(list)
    for t in transistors:
        groups[t["gate"]].append(t)

    # Create group data with transistor lists and their drain/source nodes
    group_data = []
    for gate, group_transistors in groups.items():
        drains = set(
            t["drain"]
            for t in group_transistors
            if t["drain"] not in ["supply", "ground"]
        )
        sources = set(
            t["source"]
            for t in group_transistors
            if t["source"] not in ["supply", "ground"]
        )
        nodes = drains | sources
        group_data.append({"transistors": group_transistors, "nodes": nodes})

    if not group_data:
        return []

    # Merge groups that share drain/source nodes
    uf = UnionFind(len(group_data))
    for i in range(len(group_data)):
        for j in range(i + 1, len(group_data)):
            if group_data[i]["nodes"] & group_data[j]["nodes"]:
                uf.union(i, j)

    # Identify connected components
    components = defaultdict(list)
    for i in range(len(group_data)):
        root = uf.find(i)
        components[root].append(i)

    # Compile current mirrors (at least 2 transistors)
    current_mirrors = []
    for root, indices in components.items():
        all_transistors = []
        for idx in indices:
            all_transistors.extend(group_data[idx]["transistors"])
        if len(all_transistors) >= 2:
            names = [t["name"] for t in all_transistors]
            current_mirrors.append(
                {"sub_circuit_name": "CM", "transistor_names": names}
            )

    return current_mirrors


def extract_current_mirrors(netlist_str):
    lines = netlist_str.strip().split("\n")
    transistors = parse_netlist(lines)
    pmos = [t for t in transistors if t["type"] == "pmos"]
    nmos = [t for t in transistors if t["type"] == "nmos"]
    cm_pmos = find_current_mirrors(pmos)
    cm_nmos = find_current_mirrors(nmos)
    return cm_pmos + cm_nmos


# Example usage (optional, for testing)
if __name__ == "__main__":
    netlist = """c1 a out
m1 b c supply supply pmos
m2 d c supply supply pmos
m3 e e supply supply pmos
m4 a e supply supply pmos
m5 e d ground ground nmos
m6 a d ground ground nmos
m7 f ibias c c pmos
m8 c c supply supply pmos
m9 e in1 f f pmos
m10 a in2 f f pmos
c2 out ground
m11 out b g g nmos
m12 g g ground ground nmos
m13 out a supply supply pmos
m14 b b h h nmos
m15 h g ground ground nmos
m16 d d ground ground nmos
m17 ibias ibias i i pmos
m18 i c supply supply pmos"""
    result = extract_current_mirrors(netlist)
    print(result)
