import xml.etree.ElementTree as ET
import glob
import os
from collections import defaultdict

hl2_subcircuit_name_mapping = {
    "MosfetSimpleCurrentMirror": "CM",
    "MosfetCascodeCurrentMirror": "CM",
    "MosfetWideSwingCascodeCurrentMirror": "CM",
    "MosfetFourTransistorCurrentMirror": "CM",
    "MosfetWilsonCurrentMirror": "CM",
    "MosfetImprovedWilsonCurrentMirror": "CM",
    "MosfetDifferentialPair": "DiffPair",
    "MosfetCascodedDifferentialPair": "DiffPair",
    "MosfetFoldedCascodeDifferentialPair": "DiffPair",
    "MosfetAnalogInverter": "Inverter",
    "MosfetCascodedAnalogInverter": "Inverter",
    "MosfetCascodedPMOSAnalogInverter": "Inverter",
    "MosfetCascodedNMOSAnalogInverter": "Inverter",
    "MosfetCascodePMOSAnalogInverterOneDiodeTransistor": "Inverter",
    "MosfetCascodeNMOSAnalogInverterOneDiodeTransistor": "Inverter",
    "MosfetCascodeAnalogInverterNmosDiodeTransistor": "Inverter",
    "MosfetCascodeAnalogInverterPmosDiodeTransistor": "Inverter",
    "MosfetCascodeAnalogInverterNmosCurrentMirrorLoad": "Inverter",
}


def rename(circuit_name):
    """only use for HL2 subcircuit names"""
    # remove indexing-brackets: MosfetNormalArray[19] -> MosfetNormalArray
    circuit_name = circuit_name[: circuit_name.find("[")]
    return hl2_subcircuit_name_mapping[circuit_name]


def get_hl1_cluster_labels(netlist_dir="data/netlist1/"):
    tree = ET.parse(glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0])
    root = tree.getroot()
    subcircuits = root[1]

    devices = defaultdict(set)
    for structure in root.findall(".//structure"):
        name = structure.attrib["name"]
        if name.startswith("MosfetDiodeArray"):
            for device in structure.iter("device"):
                devices["MosfetDiode"].add(device.attrib["name"].replace("/", ""))

    tree = ET.parse(glob.glob(os.path.join(netlist_dir, "partitioning_result.xml"))[0])
    root = tree.getroot()
    subcircuits = root[1]
    for cap in subcircuits.iter("capacitance"):
        # print (cap.attrib['type'].replace("/", ""))
        for device in cap.iter("device"):
            devices[cap.attrib["type"] + "_cap"].add(
                device.attrib["name"].replace("/", "")
            )
    devices = [(k, list(v)) for k, v in devices.items()]
    return devices


def get_hl2_cluster_labels(netlist_dir="data/netlist1/"):
    tree = ET.parse(glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0])
    root = tree.getroot()
    subcircuits = root[1]

    structures = []
    for sc in subcircuits:
        # ignore this label
        if (
            sc.attrib["name"].startswith("MosfetNmosDiodeAnalogInverter")
            or sc.attrib["name"].startswith("MosfetPmosDiodeAnalogInverter")
            or sc.attrib["name"].startswith("CapacitorArray")
            or sc.attrib["name"].startswith("MosfetNormalArray")
            or sc.attrib["name"].startswith("MosfetDiodeArray")
        ):
            continue
        name = rename(sc.attrib["name"])
        if name == "DiffPair":
            should_skip = False
            for pin in sc[0]:
                if pin.attrib["net"] == "/vref":
                    should_skip = True
                    break
            if should_skip:
                continue

        device_names = []
        for device in sc.iter("device"):
            device_names.append(device.attrib["name"].replace("/", ""))

        if name not in ["cap", "MosfetDiode", "Mosfet"]:
            if len(device_names) == 1:
                print("Warning: Only one device in subcircuit:", name)
                print(sc.attrib["name"])
            structures.append((name, device_names))

    structures = [(k, v) for k, v in structures]
    return structures


def get_hl3_cluster_labels(netlist_dir="data/asi-fuboco-test"):
    tree = ET.parse(glob.glob(os.path.join(netlist_dir, "partitioning_result.xml"))[0])
    root = tree.getroot()
    partitions = root[1]
    name_mappings = {
        "firstStage": "firstStage",
        "primarySecondStage": "secondStage",
        "secondarySecondStage": "secondStage",
        "thirdStage": "secondStage",
        "fourthStage": "thirdStage",
    }
    hl3_clusters = defaultdict(set)
    for par in partitions:
        if par.tag == "gmParts":
            for gm in par.iter("gmPart"):
                partition_type = name_mappings.get(gm.attrib["type"], gm.attrib["type"])
                for device in gm.iter("device"):
                    hl3_clusters[partition_type].add(
                        device.attrib["name"].replace("/", "")
                    )
        if par.tag == "loadParts":
            for loadpart in par.iter("loadPart"):
                partition_type = "loadPart"
                for device in loadpart.iter("device"):
                    hl3_clusters[partition_type].add(
                        device.attrib["name"].replace("/", "")
                    )

        if par.tag == "biasParts":
            for biaspart in par.iter("biasPart"):
                partition_type = "biasPart"
                for device in biaspart.iter("device"):
                    hl3_clusters[partition_type].add(
                        device.attrib["name"].replace("/", "")
                    )

        if par.tag == "commonModeSignalDetectorParts":
            for cmfb in par.iter("commonModeSignalDetectorPart"):
                partition_type = "commonModeSignalDetectorPart"
                for device in cmfb.iter("device"):
                    hl3_clusters[partition_type].add(
                        device.attrib["name"].replace("/", "")
                    )

        if par.tag == "positiveFeedbackParts":
            for fb in par.iter("positiveFeedbackPart"):
                partition_type = "positiveFeedbackPart"
                for device in fb.iter("device"):
                    hl3_clusters[partition_type].add(
                        device.attrib["name"].replace("/", "")
                    )

    # hl3_clusters = [
    #     {"sub_circuit_name": k, "transistor_names": list(v)}
    #     for k, v in hl3_clusters.items()
    # ]
    hl3_clusters = [(k, list(v)) for k, v in hl3_clusters.items()]
    return hl3_clusters


if __name__ == "__main__":
    print(get_hl2_cluster_labels(netlist_dir="data/asi-fuboco-test/small/2/"))
    print(get_hl3_cluster_labels(netlist_dir="data/asi-fuboco-test/small/1/"))
