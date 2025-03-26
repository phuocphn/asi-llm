import xml.etree.ElementTree as ET
import glob
tree = ET.parse(glob.glob("data/netlist10/*.xml")[0])
root = tree.getroot()


# print (root.tag)
subcircuits = root[1]
num_subcircuits = len(subcircuits)

rename_map = {
	'MosfetCascodedPMOSAnalogInverter': 'Inverter',
	'MosfetCascodedNMOSAnalogInverter': 'Inverter',
	'MosfetCascodedAnalogInverter': 'Inverter',
	'MosfetCascodeAnalogInverterPmosDiodeTransistor': 'Inverter',
	'MosfetCascodeNMOSAnalogInverterOneDiodeTransistor': 'Inverter',
	'MosfetDifferentialPair': 'DiffPair',
	'MosfetSimpleCurrentMirror': 'CM',
	'MosfetImprovedWilsonCurrentMirror': 'CM',
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


print (f"{num_subcircuits=}")
for sc in subcircuits:
	name = rename(sc.attrib['name'])
	device_names = []
	for device in sc.iter('device'):
		device_names.append(device.attrib['name'].replace("/", ""))

	sc_info = {'name': name, 'devices': device_names}
	print (sc_info)


print ("*********")
diode_connected_device_names = []
for sc in subcircuits:
	for ssc in sc.iter('structure'):
		name = ssc.attrib['name']
		if  "MosfetDiodeArray" not in name:
			# print (name)
			continue
		
		for device in ssc.iter('device'):
			diode_connected_device_names.append(device.attrib['name'].replace("/", ""))

		#sc_info = {'name': name, 'devices': device_names}
		#print (sc_info)

print (list(set(diode_connected_device_names)))