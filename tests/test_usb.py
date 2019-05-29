import unittest
import noma.usb
import platform

# Check if Mac or Linux
if platform.system() == "Linux":
    device = "sda"
    device_partition = "sda1"
else:
    device = "disk1"
    device_partition = "disk1s1"


class TestNode(unittest.TestCase):

    def test_is_mounted_device(self):
        result = noma.usb.is_mounted(device)
        self.assertIsInstance(result, bool)

    def test_is_mounted_partition(self):
        result = noma.usb.is_mounted(device_partition)
        self.assertTrue(result)

    def test_dev_size(self):
        result = noma.usb.dev_size(device)
        self.assertIsInstance(result, int)

    def test_fs_size(self):
        result = noma.usb.fs_size("/")
        self.assertIsInstance(result, int)

    def test_usb_part_size(self):
        result = noma.usb.usb_part_size(device_partition)
        self.assertIsInstance(result, int)

    def test_sd_part_size(self):
        result = noma.usb.sd_part_size(device_partition)
        self.assertIsInstance(result, int)

    def test_usb_devs(self):
        result = noma.usb.usb_devs()
        self.assertIsInstance(result, list)
        self.assertTrue(device in result)

    def test_sd_devs(self):
        result = noma.usb.sd_devs()
        self.assertIsInstance(result, list)
        # TODO: test environment requires SD device
        # self.assertEqual(result[0], "mmcblk0")

    def test_usb_partitions(self):
        result = noma.usb.usb_partitions()
        self.assertTrue(device_partition in result)

    def test_sd_partitions(self):
        result = noma.usb.sd_partitions()
        self.assertIsInstance(result, list)
        # TODO: test environment requires SD device
        # self.assertEqual(result[0], "mmcblk0")

    def test_usb_partition_table(self):
        result = noma.usb.usb_partition_table()
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.get(device_partition), int)

    def test_sd_partition_table(self):
        result = noma.usb.sd_partition_table()
        self.assertIsInstance(result, dict)
        # TODO: test environment requires SD device
        # self.assertIsInstance(result.get('mmcblk0'), int)

    def test_sd_device_table(self):
        result = noma.usb.sd_device_table()
        self.assertIsInstance(result, dict)
        # TODO: test environment requires SD device
        # self.assertIsInstance(result.get('mmcblk0'), int)

    def test_usb_device_table(self):
        result = noma.usb.usb_device_table()
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.get('sda'), int)

    def test_sort_partitions(self):
        sorted_table = noma.usb.sort_partitions()
        self.assertLessEqual(sorted_table[0][1], sorted_table[1][1])
        self.assertLessEqual(sorted_table[1][1], sorted_table[2][1])
        self.assertLessEqual(sorted_table[2][1], sorted_table[3][1])

    def test_largest_partition(self):
        result = noma.usb.largest_partition()
        sorted_partitions = noma.usb.sort_partitions()
        self.assertTrue(sorted_partitions[-1], result)

    def test_medium_partition(self):
        result = noma.usb.medium_partition()
        sorted_partitions = noma.usb.sort_partitions()
        self.assertTrue(sorted_partitions[-2], result)

    def test_smallest_partition(self):
        result = noma.usb.smallest_partition()
        sorted_partitions = noma.usb.sort_partitions()
        self.assertTrue(sorted_partitions[0], result)

    def test_largest_part_size(self):
        result = noma.usb.largest_part_size()
        largest_partition = noma.usb.sort_partitions()[-1][1]
        self.assertEqual(largest_partition, result)



# Create test suite
TestSuite = unittest.TestSuite()

TestSuite.addTest(TestNode("test_is_mounted_device"))
TestSuite.addTest(TestNode("test_is_mounted_partition"))
TestSuite.addTest(TestNode("test_fs_size"))

# Some tests are platform specific
if platform.system() == 'Linux':
    TestSuite.addTest(TestNode("test_dev_size"))
    TestSuite.addTest(TestNode("test_usb_part_size"))
    TestSuite.addTest(TestNode("test_sd_part_size"))
    TestSuite.addTest(TestNode("test_usb_devs"))
    TestSuite.addTest(TestNode("test_sd_devs"))
    TestSuite.addTest(TestNode("test_usb_partitions"))
    TestSuite.addTest(TestNode("test_sd_partitions"))
    TestSuite.addTest(TestNode("test_usb_partition_table"))
    TestSuite.addTest(TestNode("test_sd_partition_table"))
    TestSuite.addTest(TestNode("test_sd_device_table"))
    TestSuite.addTest(TestNode("test_usb_device_table"))
    TestSuite.addTest(TestNode("test_sort_partitions"))
    TestSuite.addTest(TestNode("test_largest_partition"))
    TestSuite.addTest(TestNode("test_medium_partition"))
    TestSuite.addTest(TestNode("test_smallest_partition"))
    TestSuite.addTest(TestNode("test_largest_part_size"))

if platform.system() == 'Darwin':  # Mac
    pass

runner = unittest.TextTestRunner()

runner.run(TestSuite)
