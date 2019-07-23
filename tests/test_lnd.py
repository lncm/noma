"""Test LND functions"""
import unittest
import logging
import random
import json
from unittest import mock
from noma import lnd


class TestComplete(Exception):
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
        pass

    def tearDown(self):
        pass

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
        handle.close.side_effect = TestComplete
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(TestComplete):
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
        handle.close.side_effect = TestComplete
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(TestComplete):
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
        COVERAGE IMPROVEMENT OPPORTUNITY: also test that we:
            - .rstrip() the password_str
        """

        def exists(call):
            if call == lnd.SESAME_PATH:
                return True
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                # Don't want to go into that logic either
                return True
            if call == lnd.SEED_FILENAME:
                raise TestComplete
            raise Unhappy(call)  # Should only have one of those calls

        m_exists.side_effect = exists
        m_open = mock.mock_open()
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(TestComplete):
                lnd.create_wallet()
        password_call = mock.call(lnd.SESAME_PATH, "r").read()
        self.assertIn(password_call, m_open.mock_calls)
        m_exists.assert_any_call(lnd.SESAME_PATH)
        m_open.assert_called_with(lnd.SESAME_PATH, "r")

    @mock.patch("noma.lnd.get")
    @mock.patch("os.path.exists")
    def test_generates_seed(self, m_exists, m_get):
        """
        Test that, if SESAME_PATH does exist and we were able to get the
        password_str earlier, and the SEED_FILENAME path does not exist, we
        call get() to get a new seed
        """

        def exists(call):
            if call == lnd.SESAME_PATH:
                return True
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                # Don't want to go into that logic either
                return True
            if call == lnd.SEED_FILENAME:
                return False
            raise Unhappy(call)  # Should only have one of those calls

        m_exists.side_effect = exists
        m_open = mock.mock_open()
        m_get.side_effect = TestComplete
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(TestComplete):
                lnd.create_wallet()
        m_get.assert_called_with(lnd.URL_GENSEED, verify=lnd.TLS_CERT_PATH)

    @mock.patch("noma.lnd.post")
    @mock.patch("noma.lnd.get")
    @mock.patch("os.path.exists")
    def test_saves_seed(self, m_exists, m_get, m_post):
        """
        Test that, if we used get() to generate a new seed as above, and if
        get().status_code == 200, we:
            - call the .json() method on the get() return value
            - get the "cipher_seed_mnemnonic" key in the resulting dict
            - open the file at lnd.SEED_FILENAME for writing
            - write the seed to file, one item in the cipher_seed_mnemonic
            iterable per line
            - close the file handle

        COVERAGE IMPROVEMENT OPPORUNITIES:
            - test that we actually check the status_code and do not proceed if
            the code is not 200
            - test that we correctly build the `data` dict
        """

        def exists(call):
            if call == lnd.SESAME_PATH:
                return True
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                # Don't want to go into that logic either
                return True
            if call == lnd.SEED_FILENAME:
                return False
            raise Unhappy(call)  # Should only have one of those calls

        mnemonic = ["foo", "bar", "baz"]

        class DummyResponse:
            """Mocked-up Response for our get() function"""

            status_code = 200

            def __init__(self, *args, **kwargs):
                pass

            def json(self):
                return {"cipher_seed_mnemonic": mnemonic}

        m_exists.side_effect = exists
        m_open = mock.mock_open()
        m_get.side_effect = DummyResponse
        m_post.side_effect = TestComplete
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(TestComplete):
                try:
                    lnd.create_wallet()
                except Unhappy as exc:
                    raise Unhappy(
                        "{}: {}\nget: {}\npost: {}".format(
                            exc, m_exists.mock_calls, m_get.mock_calls,
                            m_post.mock_calls)
                    )
        m_get.assert_called_with(lnd.URL_GENSEED, verify=lnd.TLS_CERT_PATH)
        handle = m_open()
        for mne in mnemonic:
            handle.write.assert_any_call(mne + "\n")
        handle.close.assert_called_with()

    @mock.patch("noma.lnd.post")
    @mock.patch("noma.lnd.get")
    @mock.patch("os.path.exists")
    def test_loads_seed(self, m_exists, m_get, m_post):
        """
        Test that, if SEED_FILENAME does exist, we:
            - do not call requests.get()
            - open lnd.SEED_FILENAME for reading
            - load every line in the resulting file into a list, stripping
            newline characters
            - build a `data` dict with the keys:
                - cipher_seed_mnemonic
                - wallet_password
            - requests.post() the `data` dict to lnd.URL_INITWALLET after
            dumping it to JSON
        COVERAGE IMPROVEMENT OPPORUNITIES:
            - test wallet_password is correctly read (earlier in the function)
        """

        def exists(call):
            if call == lnd.SESAME_PATH:
                return True
            if call == lnd.SAVE_PASSWORD_CONTROL_FILE:
                # Don't want to go into that logic either
                return True
            if call == lnd.SEED_FILENAME:
                return True
            raise Unhappy(call)  # Should only have one of those calls

        mnemonic = ["foo", "bar", "baz"]
        file_contents = "\n".join(mnemonic)
        m_exists.side_effect = exists
        m_open = mock.mock_open(read_data=file_contents)
        m_post.side_effect = TestComplete
        with mock.patch("builtins.open", m_open):
            with self.assertRaises(TestComplete):
                lnd.create_wallet()
        m_get.assert_not_called()
        m_open.assert_called_with(lnd.SEED_FILENAME, "r")
        post_call = m_post.mock_calls[-1]
        _, args, kwargs = post_call
        self.assertIn(lnd.URL_INITWALLET, args)
        self.assertEqual(kwargs["verify"], lnd.TLS_CERT_PATH)
        data_json = kwargs["data"]
        data = json.loads(data_json)
        self.assertEqual(data["cipher_seed_mnemonic"], mnemonic)


if __name__ == "__main__":
    unittest.main()
