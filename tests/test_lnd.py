"""Unit test template"""
import unittest
import logging
import random
from unittest import mock
from noma import lnd

PATCH_MODULES = [
    "requests.get",
    "requests.post",
    "base64.b64encode",
    "json.dumps",
    "os.path",
]


class Boom(Exception):
    """Raise me to stop the test, we're done"""

    pass


class Unhappy(Exception):
    """Something has gone wrong"""

    pass


class LndCreateWalletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger("root").getChild("lnd_test")

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.mocks = {mod: mock.MagicMock() for mod in PATCH_MODULES}

    def tearDown(self):
        pass

    @mock.patch("os.path.exists")
    def test_checks_path(self, m_exists):
        """Check create_walet() checks whether the SAVE_PASSWORD_CONTROL_FILE
        exists"""
        m_exists.side_effect = Boom
        with self.assertRaises(Boom):
            lnd.create_wallet()
        m_exists.assert_called_with(lnd.SAVE_PASSWORD_CONTROL_FILE)

    @mock.patch("noma.lnd.randompass")
    @mock.patch("os.path.exists")
    def test_generates_pass_and_opens_passfile(self, m_exists, m_rpass):
        """
        Test that, if SAVE_PASSWORD_CONTROL_FILE does not exist, we call
        `randompass` and open the temp password file
        """

        def pass_control(call):
            """Checking for the file happens first, if we are called with any
            other arg, something is wrong"""
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                return False
            raise Unhappy(call)

        m_exists.side_effect = pass_control
        m_open = mock.mock_open()
        m_open.side_effect = Boom
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(Boom):
                lnd.create_wallet()
        m_exists.assert_called_with(lnd.SAVE_PASSWORD_CONTROL_FILE)
        m_rpass.assert_called_with(string_length=15)
        m_open.assert_called_with(lnd.TEMP_PASSWORD_FILE_PATH, "w")

    @mock.patch("noma.lnd.randompass")
    @mock.patch("os.path.exists")
    def test_uses_tempfile_if_no_controlfile(self, m_exists, m_rpass):
        """
        Test that, if SESAME_PATH does not exist, and SAVE_PASS_CONTROL_FILE
        does not exist either, we:
            - generate the password with `randompass`,
            - open the temporary password file
            - write the generated password to the temp file, and
            - close the file
        """

        def exists(call):
            if call in (lnd.SAVE_PASSWORD_CONTROL_FILE, lnd.SESAME_PATH):
                return False
            raise Unhappy(call)  # Should only have one of those calls

        m_exists.side_effect = exists
        m_open = mock.mock_open()
        m_rpass.return_value = random.random()
        handle = m_open()
        handle.close.side_effect = Boom
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(Boom):
                lnd.create_wallet()
        m_exists.assert_any_call(lnd.SESAME_PATH)
        m_exists.assert_any_call(lnd.SAVE_PASSWORD_CONTROL_FILE)
        m_rpass.assert_called_with(string_length=15)
        m_open.assert_called_with(lnd.TEMP_PASSWORD_FILE_PATH, "w")
        handle.write.assert_called_with(m_rpass.return_value)
        handle.close.assert_called_with()

    @mock.patch("noma.lnd.randompass")
    @mock.patch("os.path.exists")
    def test_uses_sesame_if_controlfile(self, m_exists, m_rpass):
        """
        Test that, if SESAME_PATH does not exist, and SAVE_PASS_CONTROL_FILE
        does exist, we:
            - generate the password with `randompass`,
            - open the sesame file
            - write the generated password to the sesame file, and
            - close the file
        """

        def exists(call):
            if call == lnd.SESAME_PATH:
                return False
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                return True
            raise Unhappy(call)  # Should only have one of those calls

        m_exists.side_effect = exists
        m_open = mock.mock_open()
        m_rpass.return_value = random.random()
        handle = m_open()
        handle.close.side_effect = Boom
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(Boom):
                lnd.create_wallet()
        m_exists.assert_any_call(lnd.SESAME_PATH)
        m_exists.assert_any_call(lnd.SAVE_PASSWORD_CONTROL_FILE)
        m_rpass.assert_called_with(string_length=15)
        m_open.assert_called_with(lnd.SESAME_PATH, "w")
        handle.write.assert_called_with(m_rpass.return_value)
        handle.close.assert_called_with()

    @mock.patch("os.path.exists")
    def test_reads_sesame_if_exists(self, m_exists):
        """
        Test that, if SESAME_PATH does exist, we:
            - read the password_str from SESAME_PATH
            - .rstrip() the result
        """

        def exists(call):
            if call == lnd.SESAME_PATH:
                return True
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                # Don't want to go into that logic either
                return True
            raise Unhappy(call)  # Should only have one of those calls

        m_exists.side_effect = exists
        m_open = mock.mock_open()
        m_open.return_value = m_open_rv = mock.MagicMock()
        m_open_rv.read = mock.MagicMock()
        m_open_rv.read.rstrip = mock.MagicMock()
        m_open_rv.read.rstrip.side_effect = Boom
        # TODO: calling open().read().rstrip() should raise the `Boom`
        # exception but it currently does not, resulting in the code proceeding
        # to encode the password and check whether SEED_FILENAME exists, at
        # which point exists() (above) raises the `Unhappy` exception
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(Boom):
                lnd.create_wallet()
        m_exists.assert_any_call(lnd.SESAME_PATH)
        m_open.assert_called_with(lnd.SESAME_PATH, "w")
        m_open_rv.read.rstrip.assert_called_with()


if __name__ == "__main__":
    unittest.main()
