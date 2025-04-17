import xml.etree.ElementTree as ET
import glob
import os
from collections import defaultdict

rename_map = {
	'MosfetCascodedPMOSAnalogInverter': 'Inverter',
	'MosfetCascodedNMOSAnalogInverter': 'Inverter',
	'MosfetCascodedAnalogInverter': 'Inverter',
	'MosfetCascodeAnalogInverterPmosDiodeTransistor': 'Inverter',
	'MosfetCascodeAnalogInverterNmosDiodeTransistor': 'Inverter',
	'MosfetCascodeNMOSAnalogInverterOneDiodeTransistor': 'Inverter',
	"MosfetCascodePMOSAnalogInverterOneDiodeTransistor": "Inverter",
	"MosfetCascodePMOSAnalogInverterCurrentMirrorLoad": "Inverter",
	"MosfetCascodeNMOSAnalogInverterCurrentMirrorLoad": "Inverter",
	"MosfetCascodeAnalogInverterTwoCurrentMirrorLoads": "Inverter",
	'MosfetAnalogInverter': 'Inverter',
	'MosfetDifferentialPair': 'DiffPair',
	'MosfetFoldedCascodeDifferentialPair': 'DiffPair',
	"MosfetCascodedDifferentialPair": "DiffPair",
	'MosfetSimpleCurrentMirror': 'CM',
	'MosfetImprovedWilsonCurrentMirror': 'CM',
	"MosfetCascodeAnalogInverterPmosCurrentMirrorLoad": "Inverter",
	"MosfetCascodeAnalogInverterNmosCurrentMirrorLoad": "Inverter",
	"MosfetFourTransistorCurrentMirror": "CM",
	"MosfetCascodeCurrentMirror": "CM",
	"MosfetWilsonCurrentMirror": "CM",
	"MosfetWideSwingCascodeCurrentMirror": "CM",
	"InverterPmosCurrentMirrorLoad": "CM",
	'CapacitorArray': 'cap',
	'MosfetDiodeArray': 'MosfetDiode',
	'MosfetNormalArray': 'Mosfet'
}


def rename(circuit_name):
	# remove indexing-brackets: MosfetNormalArray[19] -> MosfetNormalArray
	circuit_name = circuit_name[:circuit_name.find("[")]

	for old_name, new_name in rename_map.items():
		circuit_name = circuit_name.replace(old_name, new_name)
	return circuit_name


def extract_HL2_devices(subcircuits):
	HL2_subcircuits = []
	for sc in subcircuits:
		name = rename(sc.attrib['name'])
		if name == "DiffPair":
			should_skip = False
			for pin in  sc[0]:
				#print (pin.attrib['name'], pin.attrib['net'])
				if pin.attrib['net'] == "/vref":
					should_skip = True
					break
			if should_skip:
				continue


		device_names = []
		for device in sc.iter('device'):
			device_names.append(device.attrib['name'].replace("/", ""))
		
		if name not in ["cap", "MosfetDiode", "Mosfet"]:
			if len(device_names) == 1:
				print ("Warning: Only one device in subcircuit:", name)
				print (sc.attrib['name'])
			HL2_subcircuits.append( {'sub_circuit_name': name, 'transistor_names': device_names})
	return HL2_subcircuits


def get_hl1_cluster_labels(netlist_dir="data/netlist1/"):
	tree = ET.parse(glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0])
	root = tree.getroot()
	subcircuits = root[1]

	devices = defaultdict(set)
	for sc in subcircuits:
		for ssc in sc.iter('structure'):
			name = ssc.attrib['name']
			if  "MosfetDiodeArray" in name:
				for device in ssc.iter('device'):
					devices["MosfetDiode"].add(device.attrib['name'].replace("/", ""))

	tree = ET.parse(glob.glob(os.path.join(netlist_dir, "partitioning_result.xml"))[0])
	root = tree.getroot()
	subcircuits = root[1]
	for cap in subcircuits.iter('capacitance'):
		# print (cap.attrib['type'].replace("/", ""))
		for device in cap.iter('device'):
			devices[cap.attrib['type'] + "_cap"].add(device.attrib['name'].replace("/", ""))
	return [{'sub_circuit_name': k, 'transistor_names': list(v)} for k,v in devices.items()]


def get_hl2_cluster_labels(netlist_dir="data/netlist1/"):
	tree = ET.parse(glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0])
	root = tree.getroot()
	subcircuits = root[1]
	return extract_HL2_devices(subcircuits)

if __name__ == "__main__":
	print(get_hl2_cluster_labels(netlist_dir="data/benchmark-asi-100/small/2/"))