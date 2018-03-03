"""Solution to the provided task.

To run:
    python solution.py vlans.csv requests.csv output.csv

"""

import csv
import argparse

NODE_DUMP = "VLAN: %s, devices: \n %s"
OUTPUT_MODE = "w"
NEWLINE = "\n"
DELIMITER = ","

VLAN_ID_HEADER = "vlan_id"
PRIMARY_PORT_HEADER = "primary_port"
DEVICE_ID_HEADER = "device_id"
REDUNDANCY_HEADER = "redundant"
REQUEST_ID_HEADER = "request_id"

PRIMARY_PORT = 1
SECONDARY_PORT = 0

OUTPUT_HEADER = [REQUEST_ID_HEADER, DEVICE_ID_HEADER,
                 PRIMARY_PORT_HEADER, VLAN_ID_HEADER]


class Device:
    """Class to hold device parameters."""
    def __init__(self, value, has_primary=False, has_secondary=False):
        self.value = value
        self.has_primary = has_primary
        self.has_secondary = has_secondary

    def __str__(self):
        return ("d_id: %s, has_p: %s, has_s: %s" % (
            str(self.value), str(self.has_primary), str(self.has_secondary)))


class VlanNode:
    """Class to hold VLAN port parameters."""
    def __init__(self, value):
        self.value = value
        self.devices = []
        self.next = None

    def __str__(self):
        return (NODE_DUMP % (str(self.value), str([str(d) for d in self.devices])))


def ParseDictToOrderedList(dict):
    """Turns the dictionary object into a list of VlanNode objects.
    
    The function sorts all VlanNodes and Devices in each VlanNode by their value.
    
    Args:
        dict: dictionary, mapping of vlans to devices and available ports, e.g.:
            {
                123: {
                         7: {
                              'has_primary': True,
                              'has_secondary': True
                            },
                         4: {
                              'has_primary': True,
                              'has_secondary': None
                            },
                    }
            }
    Returns:
        list of VlanNodes, sorted. E.g.
        
        [VlanNode(id: 123,
                  devices: Device(4, has_primary:True, has_secondary:None),
                           Device(7, has_primary:True, has_secondary:True))]
    """
    vlist = []
    for vlan, devices in dict.items():
        node = VlanNode(vlan)
        for id, ports in devices.items():
            device = Device(id,
                            ports.get("has_primary", False),
                            ports.get("has_secondary", False))
            node.devices.append(device)
        vlist.append(node)
        
    vlist.sort(key=lambda x: x.value)
    for v in vlist:
        v.devices.sort(key=lambda x: x.value)
    return vlist


def CreateVlanListFromFile(reader):
    """Creates a list of VlanNodes from the provided CSV file.
        
    Args:
        reader: reader iterator for file with devices and their
            available ports.
        
    Returns:
        list of VlanNodes ordered by node value.
    """
    dict = {}
    for row in reader:
        try:
            vlan_id = int(row[VLAN_ID_HEADER])
            primary_port = int(row[PRIMARY_PORT_HEADER])
            device_id = int(row[DEVICE_ID_HEADER])
        except ValueError as e:
            print(e)
            
        if vlan_id not in dict:
            dict[vlan_id] = {}
        if device_id not in dict[vlan_id]:
            dict[vlan_id][device_id] = {}
        if bool(primary_port):
            dict[vlan_id][device_id]["has_primary"] = True
        else:
            dict[vlan_id][device_id]["has_secondary"] = True
     
    return ParseDictToOrderedList(dict)


def ProcessRequests(reader, vlans):
    """Reserves vlans and devices.
    
    Args:
        reader: Reader object for file with requests.
        vlans: vlans available before any requests are made
    
    Returns:
        list of reserved Vlans and Devices if the following format:
            [[request_id, device_id, primary_port, vlan_id]]
    """
    reservations = []
    for row in reader:
        if not vlans:
            print("No more available devices to process requests farther then request id: ",
                  row[REQUEST_ID_HEADER])
            break
        if not int(row[REDUNDANCY_HEADER]):
            device_id, vlan_id = Reserve(vlans, False)
            reservations.append([row[REQUEST_ID_HEADER], device_id, PRIMARY_PORT, vlan_id])
        else:
            device_id, vlan_id = Reserve(vlans, True)
            reservations.append([row[REQUEST_ID_HEADER], device_id, SECONDARY_PORT, vlan_id])
            reservations.append([row[REQUEST_ID_HEADER], device_id, PRIMARY_PORT, vlan_id])
    return reservations


def Reserve(vlans, redundant):
    """Gets Vlan and Device ID that can be reserved.
    
    This function also removes ports that are no longer eligible for reservation.
    
    Args:
        vlans: list of VlanNodes with Device objects.
    
    Returns:
        tuple of device_id, vlan_id
    """
    if not vlans:
        return    
    for iv, vlan in enumerate(vlans):
        for id, device in enumerate(vlan.devices):
            eligible = False
            to_remove = []
            if redundant and device.has_primary and device.has_secondary:
                del(vlans[iv].devices[id])
                eligible = True
            if not redundant and device.has_primary:
               vlans[iv].devices = vlan.devices[id+1:]
               eligible = True
            if not device.has_primary:
                to_remove.append(id)
            if eligible:
                if len(vlans[iv].devices ) == 0:
                    del(vlans[iv])
                return device.value, vlan.value


def main(vlans_path, requests_path, output_path):
    vlans = None
    with open(vlans_path, newline=NEWLINE) as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        vlans = CreateVlanListFromFile(reader)\

    reservations = None
    with open(requests_path, newline=NEWLINE) as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        reservations = ProcessRequests(reader, vlans)
    if not reservations:
        print("Failed to reserve ports.")
        return

    with open(output_path, OUTPUT_MODE) as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADER)
        writer.writerows(reservations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process data with specified parameters.")
    parser.add_argument("vlans")
    parser.add_argument("requests")
    parser.add_argument("output")
    argv = parser.parse_args()
    main(argv.vlans, argv.requests, argv.output)
