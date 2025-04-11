import glob
from collections import defaultdict
from random import shuffle
import os
import shutil

def get_devices(f):
    devices = defaultdict(list)
    with open(f, "r") as f:
        for l in f:
            if ".suckt" in l or ".end" in l:
                continue
            
            device_info = l.strip().split()
            if len(device_info) > 0:
                # print (device_info)
                if device_info[0].startswith("m"):
                    devices["transistors"].append(device_info[0])
                elif device_info[0].startswith("c"):
                    devices["caps"].append(device_info[0])
            
    return devices
    

def make_benchmark():

    netlist_dir = "/mnt/home/pham/code/outputs_0/outputs/opamps-080225"
    config = {
        'max_single_output_one_stage_opamps': [50, f"{netlist_dir}/SingleOutputOpAmps/one_stage_single_output_op_amp*.ckt"] ,
        'max_single_output_two_stage_opamps': [50, f"{netlist_dir}/SingleOutputOpAmps/two_stage_single_output_op_amp*.ckt"],
        'max_single_output_symmetrical_op_amps': [50, f"{netlist_dir}/SingleOutputOpAmps/symmetrical_op_amp*.ckt"],

        'max_fully_differential_one_stage_opamps':  [50, f"{netlist_dir}/FullyDifferentialOpAmps/one_stage_fully_differential_*.ckt"],
        'max_fully_differential_two_stage_opamps': [50, f"{netlist_dir}/FullyDifferentialOpAmps/two_stage_fully_differential_*.ckt"],
        # 'max_fully_differential_three_stage_opamps': 1,

        # 'max_single_output_three_stage_opamps':  [50, f"{netlist_dir}/SingleOutputOpAmps/three_stage*.ckt"],
        # 'max_fully_differential_three_stage_opamps':  [50, f"{netlist_dir}/FullyDifferentialOpAmps/three_stage_*.ckt"],
        'max_single_output_three_stage_opamps':  [50, f"/mnt/home/pham/code/maga/outputs/TopologyGen/SingleOutputOpAmps/three_stage*.ckt"],

    }


    # three set: small / medium / large

    # small
    small_opamps_benchmarks = []
    opamp_count = defaultdict(int)
    for opamp_set, settings in config.items():

        for f in glob.glob(settings[1]):
            devices = get_devices(f)
            num_transistors = len(devices['transistors'])
            if num_transistors < 20 and opamp_count[opamp_set] < settings[0]:
                small_opamps_benchmarks.append(f)
                opamp_count[opamp_set] += 1
                print (f"added {f} to small-size opamps benchmarks")

    # assert len(small_opamps_benchmarks) > 50, f"expected more than 50 small opamps benchmarks, got {len(small_opamps_benchmarks)}"


    # medium
    medium_opamps_benchmarks = []
    opamp_count = defaultdict(int)
    for opamp_set, settings in config.items():
        for f in glob.glob(settings[1]):
            devices = get_devices(f)
            num_transistors = len(devices['transistors'])
            if (num_transistors >= 20 and num_transistors < 40) and opamp_count[opamp_set] < settings[0]:
                medium_opamps_benchmarks.append(f)
                opamp_count[opamp_set] += 1
                print (f"added {f} to medium-size opamps benchmarks")



    # large
    large_opamps_benchmarks = []
    opamp_count = defaultdict(int)
    for opamp_set, settings in config.items():
        for f in glob.glob(settings[1]):
            devices = get_devices(f)
            num_transistors = len(devices['transistors'])
            if (num_transistors >= 30 and num_transistors < 40) and opamp_count[opamp_set] < settings[0]:
                large_opamps_benchmarks.append(f)
                opamp_count[opamp_set] += 1
                print (f"added {f} to large-size opamps benchmarks")

    shuffle(small_opamps_benchmarks)
    shuffle(medium_opamps_benchmarks)
    shuffle(large_opamps_benchmarks)

    print (f"num small opamps benchmarks: {len(small_opamps_benchmarks)}")
    print (f"num medium opamps benchmarks: {len(medium_opamps_benchmarks)}")
    print (f"num large opamps benchmarks: {len(large_opamps_benchmarks)}")

    return small_opamps_benchmarks[:100], medium_opamps_benchmarks[:100], large_opamps_benchmarks[:100]





def create_data_dir():
    data_dir = "data/benchmark-asi-100"
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir)

    # create subdirectories for small, medium, and large opamps
    os.makedirs(os.path.join(data_dir, "small"))
    os.makedirs(os.path.join(data_dir, "medium"))
    os.makedirs(os.path.join(data_dir, "large"))

    return data_dir

def copy_netlist_files(benchmark_list, data_dir):
    index = 1


    for f in benchmark_list:
        os.makedirs(os.path.join(data_dir, str(index)))

        # get basename
        basename = os.path.basename(f)
        # get directory name
        dirname = os.path.dirname(f)
        # copy netlist file
        shutil.copy(f, os.path.join(data_dir, str(index)))

        # copy structural recognition result file
        structrec_file = os.path.join(dirname, "structural_recognition.result", basename.replace(".ckt", ".xml"))
        if not os.path.exists(structrec_file):
            print (f"structural_recognition.result file {structrec_file} does not exist")
        else:
            # copy structural recognition result file
            dest_f = os.path.join(data_dir, str(index), "structure_result.xml")
            shutil.copy(structrec_file, dest_f)
        
        # copy partitioning result file 
        partition_file = os.path.join(dirname, "partitioning.result", basename.replace(".ckt", ".xml"))
        if not os.path.exists(partition_file):
            print (f"partitioning.result file {partition_file} does not exist")
        else:
            dest_f = os.path.join(data_dir, str(index), "partitioning_result.xml")
            shutil.copy(partition_file,  dest_f)

        index += 1


def write_netlist_path_to_file(benchmark_list, file):
    with open(file, "w") as fw:
        for netlist in benchmark_list:
            fw.write(f"{netlist}\n")

small_opamps_benchmarks,medium_opamps_benchmarks, large_opamps_benchmarks = make_benchmark()


create_data_dir()
copy_netlist_files(small_opamps_benchmarks, "data/benchmark-asi-100/small")
copy_netlist_files(medium_opamps_benchmarks, "data/benchmark-asi-100/medium")   
copy_netlist_files(large_opamps_benchmarks, "data/benchmark-asi-100/large")


write_netlist_path_to_file(small_opamps_benchmarks, "data/benchmark-asi-100/small.txt")
write_netlist_path_to_file(medium_opamps_benchmarks, "data/benchmark-asi-100/medium.txt")  
write_netlist_path_to_file(large_opamps_benchmarks, "data/benchmark-asi-100/large.txt")