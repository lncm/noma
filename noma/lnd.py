"""
LND related functionality
"""
import pathlib
from subprocess import call, run
from os import path
from json import dumps
import base64
from requests import get, post
import noma.config as cfg


def check_wallet():
    """
    This will either import an existing seed (or our own generated one),
    or use LND to create one.
    It will also create a password either randomly or use an existing password
    provided)

    :return str: Status
    """
    if cfg.LND_PATH.exists():
        if not cfg.WALLET_PATH.exists():
            create_wallet()
        else:
            print("❌ Error: LND not initialized")
            print("Wallet already exists!")
            print("Please backup and move: " + str(cfg.WALLET_PATH))
            print("and then restart lnd")

    else:
        print("❌ Error: lnd directory does not exist!")


def encodemacaroons(macaroonfile=cfg.MACAROON_PATH, tlsfile=cfg.TLS_CERT_PATH):
    """base64url encode macaroon and TLS certificate"""
    if path.exists(str(macaroonfile)) and path.exists(str(tlsfile)):
        with open(path.expanduser(macaroonfile), "rb") as f:
            macaroon_bytes = f.read()
        with open(path.expanduser(tlsfile), "rb") as f:
            tls_bytes = f.read()
        macaroonencoded = base64.urlsafe_b64encode(macaroon_bytes)
        tlsdecoded = tls_bytes.decode("utf-8")
        tlstrim = (
            tlsdecoded.replace("\n", "")
            .replace("-----BEGIN CERTIFICATE-----", "")
            .replace("-----END CERTIFICATE-----", "")
            .replace("+", "-")
            .replace("/", "_")
            .replace("=", "")
        )
        tlsencoded = tlstrim.encode("utf-8")

        return {
            "status": "OK",
            "certificate": tlsencoded,
            "macaroon": macaroonencoded,
        }
    else:
        return {"status": "File Not Found"}


def connectstring(
    hostname=cfg.URL_GRPC,
    macaroonfile=cfg.MACAROON_PATH,
    tlsfile=cfg.TLS_CERT_PATH,
):
    """Show lndconnect string for remote wallets such as Zap"""
    result = encodemacaroons(macaroonfile, tlsfile)
    if result["status"] == "OK":
        macaroon_string = str(result["macaroon"], "utf-8")
        cert_string = str(result["certificate"], "utf-8")
        print(
            "lndconnect://"
            + hostname
            + "?cert="
            + cert_string
            + "&macaroon="
            + macaroon_string
        )
    else:
        print(result["status"])


def autounlock():
    """Auto-unlock lnd using password.txt, tls.cert"""

    password_str = open(cfg.PASSWORD_FILE_PATH, "r").read().rstrip()
    password_bytes = str(password_str).encode("utf-8")
    data = {"wallet_password": base64.b64encode(password_bytes).decode()}
    try:
        response = post(
            cfg.URL_UNLOCKWALLET, verify=cfg.TLS_CERT_PATH, data=dumps(data)
        )
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
        config_path = cfg.LND_CONF
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
        config_path = cfg.LND_CONF
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
        lnd_config = cfg.LND_CONF
    if pathlib.Path(lnd_config).is_file():
        set_kv("bitcoind.rpcuser", user, "Bitcoind", lnd_config)
        set_kv("bitcoind.rpcpass", password, "Bitcoind", lnd_config)


def autoconnect(list_path=""):
    """Auto-connect to a list of nodes in lnd/autoconnect.txt"""
    print("Connecting to:")
    if not list_path:
        list_path = pathlib.Path(cfg.LND_PATH / "autoconnect.txt")

    with open(list_path) as address_list:
        for address in address_list:
            print(address.strip())
            call(
                [
                    "docker",
                    "exec",
                    cfg.LND_MODE + "_lnd_1",
                    "lncli",
                    "connect",
                    address.strip(),
                ]
            )


def check():
    """Check lnd filesystem structure"""
    if cfg.LND_PATH.is_dir():
        print("✅ lnd directory exists")
    else:
        print("❌ lnd directory missing")

    if cfg.LND_CONF.is_file():
        print("✅ lnd.conf exists")
    else:
        print("❌ lnd.conf missing")

    if cfg.LND_PATH.is_dir() and cfg.LND_CONF.is_file():
        return True
    return False


def backup():
    """Export and backup latest channel.db from lnd via ssh"""
    # secure remote backups via scp
    if cfg.CHANNEL_BACKUP.is_file():
        # scp options:
        # -B for non-interactive batch mode
        # -p to preserve modification & access time, modes
        complete = run(["scp",
                        "-B",
                        "-i {}".format(cfg.SSH_IDENTITY),
                        "-p",
                        "-P {}".format(cfg.SSH_PORT),
                        "{}".format(cfg.CHANNEL_BACKUP),
                        "{}".format(cfg.SSH_TARGET)])
        return complete.returncode
    print("Error: channel.backup not found")
    return exit(1)


def savepeers():
    """Save list of peers to file on disk for reconnecting"""
    # TODO: export list of peers to text file on disk
    print("Not implemented yet")


def randompass(string_length=10):
    """Generate random password"""
    from random import choice
    from string import ascii_letters

    letters = ascii_letters
    return "".join(choice(letters) for i in range(string_length))


def _write_password(password_str):
    """Write a generated password to file, either the TEMP_PASSWORD_FILE_PATH
    or the PASSWORD_FILE_PATH depending on whether SAVE_PASSWORD_CONTROL_FILE
    exists."""
    if not path.exists(cfg.SAVE_PASSWORD_CONTROL_FILE):
        # Use temporary file if there is a password control file there
        temp_password_file = open(cfg.PASSWORD_FILE_PATH, "w")
        temp_password_file.write(password_str)
        temp_password_file.close()
    else:
        # Use password.txt if password_control_file exists
        password_file = open(cfg.PASSWORD_FILE_PATH, "w")
        password_file.write(password_str)
        password_file.close()


def _wallet_password():
    """Either load the wallet password from PASSWORD_FILE_PATH, or generate a new
    password, save it to file, and in either case return the password"""
    # Check if there is an existing file, if not generate a random password
    if not path.exists(cfg.PASSWORD_FILE_PATH):
        # password file doesnt exist
        password_str = randompass(string_length=15)
        _write_password(password_str)
    else:
        # Get password from file if password file already exists
        password_str = open(cfg.PASSWORD_FILE_PATH, "r").read().rstrip()
    return password_str


def _generate_and_save_seed():
    """Generate a wallet seed, save it to SEED_FILENAME, and return it"""
    mnemonic = None
    return_data = get(cfg.URL_GENSEED, verify=cfg.TLS_CERT_PATH)
    if return_data.status_code == 200:
        json_seed_creation = return_data.json()
        mnemonic = json_seed_creation["cipher_seed_mnemonic"]
        seed_file = open(cfg.SEED_FILENAME, "w")
        for word in mnemonic:
            seed_file.write(word + "\n")
        seed_file.close()
    # Data doesnt get set if cant create the seed but that is fine, handle
    # it later
    return mnemonic


def _load_seed():
    """Load the wallet seed from SEED_FILENAME and return it"""
    # Seed exists
    seed_file = open(cfg.SEED_FILENAME, "r")
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
    if not path.exists(cfg.SEED_FILENAME):
        mnemonic = _generate_and_save_seed()
    else:
        mnemonic = _load_seed()
    if mnemonic:
        # Generate init wallet file from what was posted
        return {
            "cipher_seed_mnemonic": mnemonic,
            "wallet_password": base64.b64encode(password_bytes).decode(),
        }
    return {}


def create_wallet():
    """
    1. Check if there's already a wallet. If there is, then exit.
    2. Check for password.txt
    3. If doesn't exist then check for whether we should save the password
    (SAVE_PASSWORD_CONTROL_FILE exists) or not
    4. If password.txt exists import password in.
    5. If password.txt doesn't exist and we don't save the password, create a
    password and save it in temporary path as defined in PASSWORD_FILE_PATH
    6. Now start the wallet creation. Look for a seed defined in SEED_FILENAME,
    if not existing then generate a wallet based on the seed by LND.
    """
    password_str = _wallet_password()

    # Step 1 get seed from web or file
    data = _wallet_data(password_str)

    # Step 2: Create wallet
    if data:
        # Data is defined so proceed
        return_data = post(
            cfg.URL_INITWALLET, verify=cfg.TLS_CERT_PATH, data=dumps(data)
        )
        if return_data.status_code == 200:
            print("✅ Create wallet is successful")
        else:
            print("❌ Create wallet is not successful")
    else:
        print("❌ Error: cannot proceed, wallet data is not defined")


if __name__ == "__main__":
    print("This file is not meant to be run directly")
