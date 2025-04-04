import xml.etree.ElementTree as ET
import glob
import os

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
	'MosfetAnalogInverter': 'Inverter',
	'MosfetDifferentialPair': 'DiffPair',
	'MosfetFoldedCascodeDifferentialPair': 'DiffPair',
	'MosfetSimpleCurrentMirror': 'CM',
	'MosfetImprovedWilsonCurrentMirror': 'CM',
	"MosfetCascodeAnalogInverterPmosCurrentMirrorLoad": "CM",
	"MosfetCascodeAnalogInverterNmosCurrentMirrorLoad": "CM",
	"MosfetFourTransistorCurrentMirror": "CM",
	"MosfetCascodeCurrentMirror": "CM",
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
		HL2_subcircuits.append( {'sub_circuit_name': name, 'transistor_names': device_names})
	return HL2_subcircuits


def get_hl1_cluster_labels(netlist_dir="data/netlist1/"):
	tree = ET.parse(glob.glob(os.path.join(netlist_dir, "*.xml"))[0])
	root = tree.getroot()
	subcircuits = root[1]

	diode_connected_device_names = []
	for sc in subcircuits:
		for ssc in sc.iter('structure'):
			name = ssc.attrib['name']
			if  "MosfetDiodeArray" not in name:
				continue
			
			for device in ssc.iter('device'):
				diode_connected_device_names.append(device.attrib['name'].replace("/", ""))

	diode_connected_device_names =  list(set(diode_connected_device_names))
	return [{'sub_circuit_name': 'MosfetDiode', 'transistor_names': [dd for dd in diode_connected_device_names]}]


def filter_HL1_blocks(HL2_blocks):
	blocks = []
	for b2 in HL2_blocks:
		if b2["sub_circuit_name"] not in ["cap", "MosfetDiode", "Mosfet"]:
			blocks.append(b2)
	return blocks


def get_hl2_cluster_labels(netlist_dir="data/netlist1/"):
	tree = ET.parse(glob.glob(os.path.join(netlist_dir, "*.xml"))[0])
	root = tree.getroot()
	subcircuits = root[1]
	# num_subcircuits = lexxn(subcircuits)
	cluster_labels = filter_HL1_blocks(extract_HL2_devices(subcircuits))
	# print (cluster_labels)

	def check_exist_in_cm(cluster_labels, tran_name):
		exist = False
		for cl in cluster_labels:
			if cl["sub_circuit_name"] == "CM" and tran_name in cl["transistor_names"]:
				exist = True
				break
		return exist

	for i, cl in enumerate(cluster_labels):
		if cl["sub_circuit_name"] == "Inverter":
			for tran in cl["transistor_names"]:
				if check_exist_in_cm(cluster_labels, tran):
					cluster_labels[i]["transistor_names"].remove(tran)

	return cluster_labels

def test():
	print (f"{num_subcircuits=}")
	print ("Diode connected devices:")
	print (extract_diode_connected_devices(subcircuits))
	print ("HL2 devices:")
	# print (extract_HL2_devices(subcircuits))
	for subcircuit in filter_HL1_blocks(extract_HL2_devices(subcircuits)):
		print (subcircuit)


	print (filter_HL1_blocks(extract_HL2_devices(subcircuits)))

if __name__ == "__main__":
	print(get_hl2_cluster_labels(netlist_dir="data/netlist1/"))