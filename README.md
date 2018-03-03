# assign_vlans

The program will take vlans.csv and requests.csv as input and produce an output.csv file that specifies which requests reserved which VLAN IDs on which port and device. 

We have incoming requests to reserve VLAN IDs for later use. Once a request reserves a VLAN ID on a particular port and device, no other request may reserve that VLAN ID on that port and device. 

There are two types of requests:
1) Requests that do not require redundancy - for these we would like to reserve a single VLAN ID that meets the following criteria:
a) The VLAN ID should be the lowest available VLAN ID on any primary port.
b) In the event of a tie, we would choose the VLAN ID on the device with the lowest
device ID
2) Requests that require redundancy - for these we would like to reserve a pair of VLAN
IDs that meet the following criteria:
a) One VLAN ID must be from a primary port and the other must be from a
secondary port
b) The two ports must be on the same device
c) The VLAN IDs must be the same on both ports
d) The VLAN IDs should be the lowest possible IDs that meet the above criteria
e) Again, in the event of a tie, we would choose the VLAN IDs on the device with
the lowest device ID
