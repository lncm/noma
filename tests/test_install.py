import unittest
import noma.install
import platform
import os
import pathlib

# Check if Mac or Linux
if platform.system() == "Linux":
    device = "sda"
    device_partition = "sda1"
else:
    device = "disk1"
    device_partition = "disk1s1"

# Set to True to enable testing SD cards
mmc_device = True

test_dir = 'test_dir_delete_me'
install_file = 'install_check_delete_me'
cache_dir = "test_cache"
var_cache = "test_cache_dest"
cache_test_file = "cache_test_file"


class TestNode(unittest.TestCase):

    def setUp(self):
        # TODO: Create block devices for testing
        pathlib.Path(install_file).touch()
        pathlib.Path(cache_dir).mkdir()
        pathlib.Path(var_cache).mkdir()
        pathlib.Path(cache_test_file).touch()

    def tearDown(self):
        # create_dir
        if pathlib.Path(test_dir).exists():
            os.rmdir(test_dir)
        # check_installed
        if pathlib.Path(install_file).exists():
            os.remove(install_file)
        # move_cache
        if pathlib.Path(cache_dir).exists():
            os.rmdir(cache_dir)
        if pathlib.Path(var_cache).exists():
            import shutil
            shutil.rmtree(var_cache, ignore_errors=True)

    def test_create_dir(self):
        result = noma.install.create_dir(test_dir)
        self.assertTrue(result)
        test_path = pathlib.Path(test_dir)
        self.assertTrue(test_path.exists())

    def test_check_installed(self):
        result = noma.install.check_installed(install_file)
        self.assertTrue(result)

    def test_move_cache(self):
        # requires Alpine's setup-apkcache utility
        result = noma.install.move_cache(cache_dir="test_cache", var_cache="test_cache_dest")
        self.assertTrue(result)
        destination = pathlib.Path(var_cache)
        self.assertTrue(pathlib.Path(destination / cache_test_file).exists())

    def test_enable_swap(self):
        # requires Alpine's rc-update utility
        result = noma.install.enable_swap()
        self.assertTrue(result)

    # def test_install_firmware(self):
    #     result = noma.install.install_firmware()
    #     self.assertTrue(result)


# Create test suite
TestSuite = unittest.TestSuite()

TestSuite.addTest(TestNode("test_create_dir"))
TestSuite.addTest(TestNode("test_check_installed"))
TestSuite.addTest(TestNode("test_move_cache"))
TestSuite.addTest(TestNode("test_install_firmware"))


# Some tests are platform specific
if platform.system() == 'Linux':
    TestSuite.addTest(TestNode("test_enable_swap"))  # requires Alpine

if platform.system() == 'Darwin':  # Mac
    pass

runner = unittest.TextTestRunner()

runner.run(TestSuite)
