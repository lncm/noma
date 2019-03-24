from subprocess import call
import os
import pathlib
from noma import rpcauth


def start():
    """Start bitcoind docker compose container"""
    from noma.node import is_running
    if is_running("bitcoind"):
        print("bitcoind is running already")
    else:
        call(["docker", "start", "compose_bitcoind_1"])


def stop():
    """Stop bitcoind docker compose container, if running"""
    from noma.node import is_running
    if is_running("bitcoind"):
        call(["docker", "exec", "compose_bitcoind_1", "bitcoin-cli", "stop"])
    else:
        print("bitcoind is already stopped")


def gen_rpcauth(username, password):
    """Generate rpcauth username and password for bitcoind"""
    rpcauth.main(username, password)


def fastsync():
    """
    Download blocks and chainstate snapshot

    :return str: Status
    """
    bitcoind_dir_path = "/media/archive/archive/bitcoin/"
    location = "http://utxosets.blob.core.windows.net/public/"
    snapshot = "utxo-snapshot-bitcoin-mainnet-565305.tar"
    url = location + snapshot
    bitcoind_dir = pathlib.Path(bitcoind_dir_path)
    bitcoind_dir_exists = bitcoind_dir.is_dir()
    print("Checking if snapshot archive exists")
    if bitcoind_dir_exists:
        print("Bitcoin directory exists")
        snapshot_file = bitcoind_dir / 'snapshot'
        if snapshot_file.is_file():
            print("Snapshot archive exists")
            if pathlib.Path(bitcoind_dir + "blocks").is_dir():
                print("Bitcoin blocks directory exists, exiting")
                exit(0)
            else:
                # Assumes download was interrupted
                print("Continue downloading snapshot")
                call(["wget", "-c", url])
                call(["tar", "xvf", snapshot])
    else:
        print("Bitcoin directory does not exist, creating")
        if pathlib.Path("/media/archive/archive").is_dir():
            pathlib.Path(bitcoind_dir).mkdir()
            os.chdir(bitcoind_dir)
            call(["wget", "-c", url])
            call(["tar", "xvf", snapshot])
        else:
            print("Error: archive directory does not exist on your usb device")
            print("Are you sure it was installed correctly?")
            exit(1)


def check():
    """Check bitcoind filesystem structure"""
    bitcoind_dir = "/media/archive/archive/bitcoin"
    bitcoind_dir_exists = pathlib.Path(bitcoind_dir).is_dir()

    if bitcoind_dir_exists:
        print("bitcoind directory exists")
    else:
        print("bitcoin folder missing")

    bitcoind_conf = "/media/archive/archive/bitcoin/bitcoin.conf"
    bitcoind_conf_exists = pathlib.Path(bitcoind_conf).is_file()

    if bitcoind_conf_exists:
        print("bitcoin.conf exists")
    else:
        print("bitcoin.conf missing")


def get_kv(key, config_path):
    """
    Parse key-value config files and print out values

    :param key: left part of key value pair
    :param config_path: path to file
    :return: value of key
    """
    import itertools
    import configparser

    parser = configparser.ConfigParser(strict=False)
    with open(config_path) as lines:
        lines = itertools.chain(("[main]",), lines)   # workaround: prepend dummy section
        parser.read_file(lines)
        return parser.get('main', key)


def set_kv(key, value, config_path):
    """
    Set key to value in path
    kv pairs are separated by "="

    :param key: key to set
    :param value: value to set
    :param config_path: config file path
    :return str: string written
    """
    from fileinput import FileInput
    import pathlib

    p = pathlib.Path(config_path)
    config_exists = p.is_file()

    if not config_exists:
        # create empty config file
        p.touch()

    current_val = None
    try:
        current_val = get_kv(key, config_path)
    except Exception as err:
        print(err)
    if value == current_val:
        # nothing to do
        print("%s already set to %s" % (key, value))
        return
    if current_val is None:
        # key does not exist yet
        with open(config_path, 'a') as file:
            # append kv pair to file
            file.write("\n%s=%s" % (key, value))
    else:
        with FileInput(config_path, inplace=True, backup='.bak') as file:
            for line in file:
                print(line.replace(current_val, value), end='')


if __name__ == "__main__":
    print("This file is not meant to be run directly")
