import json
from src.netlist import SPICENetlist


if __name__ == "__main__":
    for i in range(1, 101, 1):
        data = SPICENetlist(f"data/asi-fuboco-test/small/{i}/")
        print(i, data.num_transistors)
