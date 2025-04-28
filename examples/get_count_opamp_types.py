import os
import glob

from collections import defaultdict


def get_count(dir="data/asi-fuboco-test/small/"):
    opamps = defaultdict(int)
    for i in range(1, 101, 1):
        for file in glob.glob(os.path.join(dir, str(i), "*.ckt")):
            file = file[: file.find("_op_amp")]
            file = os.path.basename(file)
            # print(file)
            opamps[file] += 1
    print(opamps)


get_count(dir="data/asi-fuboco-test/small/")
get_count(dir="data/asi-fuboco-test/medium/")
get_count(dir="data/asi-fuboco-test/large/")
