"""
LND related functionality
"""
from os import path
from subprocess import call
import pathlib
import shutil


def check_wallet():
    """
    This will either import an existing seed (or our own generated one),
    or use LND to create one.
    It will also create a password either randomly or use an existing password provided)

    :return str: Status
    """
    if path.exists("/media/important/important/lnd"):
        if not path.exists("/media/important/important/lnd/data/chain"):
            create_wallet()
        else:
            print("Wallet already exists!")
            print(
                "Please backup and move /media/important/important/lnd/data/chain and then restart lnd"
            )
    else:
        print("lnd directory does not exist!")


def autounlock():
    """Autounlock lnd using sesame.txt, tls.cert"""
    from json import dumps
    from requests import post
    from base64 import b64encode

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
            # JSON will fail to decode when unlocked already since response is empty
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
    """Create lnd directory structure and config file"""
    lnd_path = "/media/important/important/lnd/"
    pathlib.Path(lnd_path).mkdir(exist_ok=True)
    shutil.copy("/home/lncm/lnd/lnd.conf", lnd_path + "/lnd.conf")


def create_wallet():
    """
    Documented logic

    1. Check if there's already a wallet. If there is, then exit.
    2. Check for sesame.txt
    3. If doesn't exist then check for whether we should save the password
    (save_password_control_file exists) or not
    4. If sesame.txt exists import password in.
    5. If sesame.txt doesn't exist ans we don't save the password, create a
    password and save it in temporary path as defined in temp_password_file_path
    6. Now start the wallet creation. Look for a seed defined in seed_filename,
    if not existing then generate a wallet based on the seed by LND.

    Main entrypoint function

    Testing creation notes:
    rm /home/lncm/seed.txt
    rm /media/important/important/lnd/sesame.txt

    docker stop compose_lndbox_1
    rm -fr /media/important/important/lnd/data/chain/
    docker start compose_lndbox_1
    """
    from requests import get, post
    from base64 import b64encode
    from json import dumps

    # Generate seed
    url = "https://localhost:8181/v1/genseed"
    # Initialize wallet
    url2 = "https://localhost:8181/v1/initwallet"
    cert_path = "/media/important/important/lnd/tls.cert"
    seed_filename = "/home/lncm/seed.txt"
    data = None

    # save password control file (Add this file if we want to save passwords)
    save_password_control_file = "/home/lncm/save_password"
    # Create password for writing
    temp_password_file_path = "/home/lncm/password.txt"

    if not path.exists(save_password_control_file):
        # Generate password but dont save it in usual spot
        password_str = randompass(string_length=15)
        temp_password_file = open(temp_password_file_path, "w")
    # Check if there is an existing file, if not generate a random password
    if not path.exists("/media/important/important/lnd/sesame.txt"):
        # sesame file doesnt exist
        password_str = randompass(string_length=15)
        if not path.exists(save_password_control_file):
            # Use tempory file if there is a password control file there
            temp_password_file = open(temp_password_file_path, "w")
            temp_password_file.write(password_str)
            temp_password_file.close()
        else:
            # Use sesame.txt if password_control_file exists
            password_file = open(
                "/media/important/important/lnd/sesame.txt", "w"
            )
            password_file.write(password_str)
            password_file.close()
    else:
        # Get password from file if sesame file already exists
        password_str = (
            open("/media/important/important/lnd/sesame.txt", "r")
            .read()
            .rstrip()
        )

    # Convert password to byte encoded
    password_bytes = str(password_str).encode("utf-8")

    # Step 1 get seed from web or file

    # Send request to generate seed if seed file doesnt exist
    if not path.exists(seed_filename):
        r = get(url, verify=cert_path)
        if r.status_code == 200:
            json_seed_creation = r.json()
            json_seed_mnemonic = json_seed_creation["cipher_seed_mnemonic"]
            seed_file = open(seed_filename, "w")
            for word in json_seed_mnemonic:
                seed_file.write(word + "\n")
            seed_file.close()
            data = {
                "cipher_seed_mnemonic": json_seed_mnemonic,
                "wallet_password": b64encode(password_bytes).decode(),
            }
        # Data doesnt get set if cant create the seed but that is fine, handle it later
    else:
        # Seed exists
        seed_file = open(seed_filename, "r")
        seed_file_words = seed_file.readlines()
        import_file_array = []
        for importword in seed_file_words:
            import_file_array.append(importword.replace("\n", ""))
        # Generate init wallet file from what was posted
        data = {
            "cipher_seed_mnemonic": import_file_array,
            "wallet_password": b64encode(password_bytes).decode(),
        }

    # Step 2: Create wallet

    if data:
        # Data is defined so proceed
        r2 = post(url2, verify=cert_path, data=dumps(data))
        if r2.status_code == 200:
            # If create wallet was successful
            print("Create wallet is successful")
        else:
            print("Create wallet is not successful")
    else:
        print("Error: cannot proceed, wallet data is not defined")


if __name__ == "__main__":
    print("This file is not meant to be run directly")
