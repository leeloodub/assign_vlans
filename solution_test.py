"""Tests for customers.py"""

import unittest

import solution


class Test(unittest.TestCase):

    def assertVlanNodeListEqual(self, actual, expected):
        for a, e in zip(actual, expected):
            self.assertEqual(a.value, e.value)
            for ad, ed in zip (a.devices, e.devices):
                self.assertDictEqual(ad.__dict__, ed.__dict__)
     
    def setUp(self):
        c1 = solution.DEVICE_ID_HEADER
        c2 = solution.PRIMARY_PORT_HEADER
        c3 = solution.VLAN_ID_HEADER
        self.vlans_csv_reader = [{c1: "0", c2: "1", c3: "8"},
                                 {c1: "3", c2: "1", c3: "1"},
                                 {c1: "0", c2: "1", c3: "2"},
                                 {c1: "0", c2: "1", c3: "5"},
                                 {c1: "0", c2: "0", c3: "2"},
                                 {c1: "1", c2: "0", c3: "6"},
                                 {c1: "1", c2: "0", c3: "8"},
                                 {c1: "2", c2: "1", c3: "8"}]
          
        v0 = solution.VlanNode(1)
        v0.devices = [solution.Device(3, True, False)]
        v1 = solution.VlanNode(2)
        v1.devices = [solution.Device(0, True, True)]
        v2 = solution.VlanNode(5)
        v2.devices = [solution.Device(0, True, False)]
        v3 = solution.VlanNode(6)
        v3.devices = [solution.Device(1, False, True)]
        v4 = solution.VlanNode(8)
        v4.devices = [solution.Device(0, True, False),
                      solution.Device(1, False, True),
                      solution.Device(2, True, False)]
        self.available_vlans = [v0, v1, v2, v3, v4]
       
    def testCreateVlanListFromFile(self):
        actual = solution.CreateVlanListFromFile(self.vlans_csv_reader)
        self.assertVlanNodeListEqual(actual, self.available_vlans)
        
    
    def testParseDictToList(self):
        input = {123: {7: {'has_primary': True, 'has_secondary': True}, 4: {'has_primary': True}}}
        v1 = solution.VlanNode(123)
        v1.devices = [solution.Device(4, True, False),
                      solution.Device(7, True, True)]
        expected = [v1]
        actual = solution.ParseDictToOrderedList(input)
        self.assertVlanNodeListEqual(actual, expected)
        
    def testReserveNonRedundant(self):
        available_vlans = self.available_vlans
        expected = (3, 1)
        actual = solution.Reserve(available_vlans, False)
        
        self.assertEqual(actual[0], expected[0])
        self.assertEqual(actual[1], expected[1])

    def testReserveRedundant(self):
        available_vlans = self.available_vlans
        expected = (0, 2)
        actual = solution.Reserve(available_vlans, True)
    
        self.assertEqual(actual[0], expected[0])
        self.assertEqual(actual[1], expected[1])
       
    def testReserveRedundant_None(self):
        self.assertIsNone(solution.Reserve(self.available_vlans[3:], True))
 
    def testUnavailableVlansRemovedForNonRedundant(self):
        available_vlans = self.available_vlans
        final_vlans = available_vlans[1:]
        solution.Reserve(available_vlans, False)
        self.assertVlanNodeListEqual(available_vlans, final_vlans)
        
    def testUnavailableVlansRemovedForRedundant(self):
        available_vlans = self.available_vlans
        final_vlans = available_vlans[0:1] + available_vlans[2:]
        solution.Reserve(available_vlans, True)
        self.assertVlanNodeListEqual(available_vlans, final_vlans)
    
if __name__ == '__main__':
    unittest.main()