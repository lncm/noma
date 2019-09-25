import unittest
import urllib3
import requests
import noma.node


class TestNode(unittest.TestCase):
    def testIsRunning(self):
        try:
            result = noma.node.is_running("bitcoind")
            self.assertFalse(result)
        except FileNotFoundError as e:
            print("Error: file not found")
            print(e)
            raise
        except urllib3.exceptions.ProtocolError as e:
            print("Error: urllib3")
            print(e)
            raise
        except requests.exceptions.ConnectionError as e:
            print("Error: requests")
            print(e)
            raise

    # def testVoltage(self):
    #     try:
    #         result = noma.node.voltage("core")
    #         self.assertIsInstance(result, str)
    #     except FileNotFoundError as e:
    #         print("Error: file not found")
    #         print(e)
    #         raise

    def testSwap(self):
        result = noma.node.get_swap()
        self.assertIsInstance(result, int)

    def testRam(self):
        result = noma.node.get_ram()
        self.assertIsInstance(result, int)

    def testTemp(self):
        result = noma.node.temp()
        self.assertIsInstance(result, int)


# Create test suite
TestSuite = unittest.TestSuite()


TestSuite.addTest(TestNode("testIsRunning"))
TestSuite.addTest(TestNode("testVoltage"))
TestSuite.addTest(TestNode("testSwap"))
TestSuite.addTest(TestNode("testRam"))


runner = unittest.TextTestRunner()

runner.run(TestSuite)
