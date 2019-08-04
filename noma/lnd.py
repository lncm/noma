"""
LND related functionality
"""
import pathlib
import shutil
from subprocess import call
from os import path
from json import dumps
from base64 import b64encode
from requests import get, post


def check_wallet():
    """
    This will either import an existing seed (or our own generated one),
    or use LND to create one.
    It will also create a password either randomly or use an existing password
    provided)

    :return str: Status
    """
    if path.exists("/media/noma/lnd"):
        if not path.exists("/media/noma/lnd/data/chain"):
            create_wallet()
        else:
            print("Wallet already exists!")
            print(
                "Please backup and move "
                "/media/noma/lnd/data/chain and then "
                "restart lnd"
            )
    else:
        print("lnd directory does not exist!")


def autounlock():
    """Autounlock lnd using sesame.txt, tls.cert"""

    url = "https://localhost:8181/v1/unlockwallet"
    cert_path = "/media/important/important/lnd/tls.cert"
    password_str = (
        open("/media/important/important/lnd/sesame.txt", "r").read().rstrip()
    )
    password_bytes = str(password_str).encode("utf-8")
    data = {"wallet_password": b64encode(password_bytes).decode()}
    try:
        response = post(url, verify=cert_path, data=dumps(data))
    except Exception:
        # Silence connection errors when lnd is not running
        pass
    else:
        try:
            print(response.json())
        except Exception:
            # JSON will fail to decode when unlocked already since response is
            # empty
            pass


def get_kv(key, section="", config_path=""):
    """
    Parse key-value config files and print out values

    :param key: left part of key value pair
    :param config_path: path to config file
    :param section: [section] of the kv pair
    :return: value of key
    """
    from configparser import ConfigParser

    if not config_path:
        config_path = "/media/important/important/lnd/lnd.conf"
    if not section:
        section = "Application Options"

    parser = ConfigParser(strict=False)
    with open(config_path) as lines:
        parser.read_file(lines)
        return parser.get(section, key)


def set_kv(key, value, section="", config_path=""):
    """
    Parse key-value config files and write them out with a key-value change

    Note: comments are lost!

    :param key: left part of key value pair
    :param value: right part of key value pair
    :param section: optional name of section to set in
    :param config_path: path to file

    :return:
    """
    from configparser import ConfigParser

    if not section:
        section = "Application Options"
    if not config_path:
        config_path = "/media/important/important/lnd/lnd.conf"
    parser = ConfigParser(strict=False)
    with open(config_path) as lines:
        parser.read_file(lines)
        parser.set(section, key, value)
        with open(config_path, "w") as file:
            parser.write(file, space_around_delimiters=False)
            file.close()


def setup_tor(version=""):
    """Add tor hidden service to lnd"""
    if not version:
        version = "v3"
    hostname_path = "/var/lib/tor/lnd-{}/hostname".format(version)
    try:
        print("Adding externalip directive to lnd for tor")
        with open(hostname_path, "r") as hostname:
            set_kv("externalip", hostname.read(), "Application Options")
    except Exception as error:
        print(error.__class__.__name__, ":", error)


def set_bitcoind(password, user="", lnd_config=""):
    """Add bitcoind rpc username and password to lnd"""
    if not user:
        user = "lncm"
    if not lnd_config:
        lnd_config = "/media/important/important/lnd/lnd.conf"
    if pathlib.Path(lnd_config).is_file():
        set_kv("bitcoind.rpcuser", user, "Bitcoind", lnd_config)
        set_kv("bitcoind.rpcpass", password, "Bitcoind", lnd_config)


def autoconnect(list_path=""):
    """Autoconnect to a list of nodes in autoconnect.txt"""
    print("Connecting to:")
    if not list_path:
        list_path = "/media/important/important/autoconnect.txt"

    with open(list_path) as address_list:
        for address in address_list:
            print(address.strip())
            call(
                [
                    "docker",
                    "exec",
                    "compose_lnd_1",
                    "lncli",
                    "connect",
                    address.strip(),
                ]
            )


def check():
    """Check lnd filesystem structure"""

    # check lnd filesystem structure
    lnd_dir = pathlib.Path("/media/important/important/lnd").is_dir()
    if lnd_dir:
        print("lnd directory exists")
    else:
        print("lnd directory missing")

    lnd_conf = pathlib.Path(
        "/media/important/important/lnd/lnd.conf"
    ).is_file()
    if lnd_conf:
        print("lnd conf exists")
    else:
        print("lnd conf missing")

    if lnd_dir and lnd_conf:
        return True
    return False


def randompass(string_length=10):
    """Generate random password"""
    from random import choice
    from string import ascii_letters

    letters = ascii_letters
    return "".join(choice(letters) for i in range(string_length))


def create():
    from noma.config import HOME

    """Create lnd directory structure and config file"""
    lnd_path = "/media/noma/lnd/"
    pathlib.Path(lnd_path).mkdir(exist_ok=True)
    shutil.copy("/media/noma/lnd/neutrino/lnd.conf", lnd_path + "/lnd.conf")


# Generate seed
URL_GENSEED = "https://localhost:8080/v1/genseed"

# Initialize wallet
URL_INITWALLET = "https://localhost:8080/v1/initwallet"

TLS_CERT_PATH = "/media/noma/lnd/neutrino/tls.cert"
SEED_FILENAME = "/media/noma/seed.txt"

# save password control file (Add this file if we want to save passwords)
SAVE_PASSWORD_CONTROL_FILE = "/media/noma/lnd/save_password"

# Create password for writing
TEMP_PASSWORD_FILE_PATH = "/media/noma/lnd/password.txt"

SESAME_PATH = "/media/noma/lnd/sesame.txt"


def _write_password(password_str):
    """Write a generated password to file, either the TEMP_PASSWORD_FILE_PATH
    or the SESAME_PATH depending on whether SAVE_PASSWORD_CONTROL_FILE
    exists."""
    if not path.exists(SAVE_PASSWORD_CONTROL_FILE):
        # Use tempory file if there is a password control file there
        temp_password_file = open(TEMP_PASSWORD_FILE_PATH, "w")
        temp_password_file.write(password_str)
        temp_password_file.close()
    else:
        # Use sesame.txt if password_control_file exists
        password_file = open(SESAME_PATH, "w")
        password_file.write(password_str)
        password_file.close()


def _wallet_password():
    """Either load the wallet password from SESAME_PATH, or generate a new
    password, save it to file, and in either case return the password"""
    # Check if there is an existing file, if not generate a random password
    if not path.exists(SESAME_PATH):
        # sesame file doesnt exist
        password_str = randompass(string_length=15)
        _write_password(password_str)
    else:
        # Get password from file if sesame file already exists
        password_str = open(SESAME_PATH, "r").read().rstrip()
    return password_str


def _generate_and_save_seed():
    """Generate a wallet seed, save it to SEED_FILENAME, and return it"""
    mnemonic = None
    return_data = get(URL_GENSEED, verify=TLS_CERT_PATH)
    if return_data.status_code == 200:
        json_seed_creation = return_data.json()
        mnemonic = json_seed_creation["cipher_seed_mnemonic"]
        seed_file = open(SEED_FILENAME, "w")
        for word in mnemonic:
            seed_file.write(word + "\n")
        seed_file.close()
    # Data doesnt get set if cant create the seed but that is fine, handle
    # it later
    return mnemonic


def _load_seed():
    """Load the wallet seed from SEED_FILENAME and return it"""
    # Seed exists
    seed_file = open(SEED_FILENAME, "r")
    seed_file_words = seed_file.readlines()
    mnemonic = []
    for importword in seed_file_words:
        mnemonic.append(importword.replace("\n", ""))
    return mnemonic


def _wallet_data(password_str):
    """Build and return the wallet `data` dict with the mnemonic and wallet
    password"""
    # Convert password to byte encoded
    password_bytes = str(password_str).encode("utf-8")
    # Send request to generate seed if seed file doesnt exist
    if not path.exists(SEED_FILENAME):
        mnemonic = _generate_and_save_seed()
    else:
        mnemonic = _load_seed()
    if mnemonic:
        # Generate init wallet file from what was posted
        return {
            "cipher_seed_mnemonic": mnemonic,
            "wallet_password": b64encode(password_bytes).decode(),
        }
    return {}


def create_wallet():
    """
    Documented logic

    1. Check if there's already a wallet. If there is, then exit.
    2. Check for sesame.txt
    3. If doesn't exist then check for whether we should save the password
    (SAVE_PASSWORD_CONTROL_FILE exists) or not
    4. If sesame.txt exists import password in.
    5. If sesame.txt doesn't exist ans we don't save the password, create a
    password and save it in temporary path as defined in
    TEMP_PASSWORD_FILE_PATH
    6. Now start the wallet creation. Look for a seed defined in SEED_FILENAME,
    if not existing then generate a wallet based on the seed by LND.

    Main entrypoint function

    Testing creation notes:
    rm $HOME/seed.txt
    rm /media/important/important/lnd/sesame.txt

    docker stop compose_lndbox_1
    rm -fr /media/important/important/lnd/data/chain/
    docker start compose_lndbox_1
    """
    password_str = _wallet_password()

    # Step 1 get seed from web or file
    data = _wallet_data(password_str)

    # Step 2: Create wallet
    if data:
        # Data is defined so proceed
        return_data = post(
            URL_INITWALLET, verify=TLS_CERT_PATH, data=dumps(data)
        )
        if return_data.status_code == 200:
            # If create wallet was successful
            print("Create wallet is successful")
        else:
            print("Create wallet is not successful")
    else:
        print("Error: cannot proceed, wallet data is not defined")


if __name__ == "__main__":
    print("This file is not meant to be run directly")
