"""
bitcoind related functionality
"""
from subprocess import call, run, PIPE, STDOUT, DEVNULL
import os
import pathlib
import shutil
import toml
from configobj import ConfigObj
from noma import rpcauth
from noma import config as cfg


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


def fastsync():
    """
    Download blocks and chainstate snapshot

    :return bool: success status
    """
    bitcoind_dir_path = "/media/archive/archive/bitcoin/"
    bitcoind_dir = pathlib.Path(bitcoind_dir_path)
    location = "http://utxosets.blob.core.windows.net/public/"
    snapshot = "utxo-snapshot-bitcoin-mainnet-565305.tar"
    checksum = (
        "8e18176138be351707aee95f349dd1debc714cc2cc4f0c76d6a7380988bf0d22"
    )
    snapshot_path = bitcoind_dir / snapshot
    url = location + snapshot

    bitcoind_dir_exists = bitcoind_dir.is_dir()

    def set_permissions(working_path):
        print("Setting file and directory permissions")
        for path, dirs, files in os.walk(working_path):
            lncm_uid, lncm_gid = 1001, 1001
            for directory in dirs:
                os.chown(os.path.join(path, directory), lncm_uid, lncm_gid)
                os.chmod(os.path.join(path, directory), 0o755)
            for file in files:
                os.chown(os.path.join(path, file), lncm_uid, lncm_gid)
                os.chmod(os.path.join(path, file), 0o744)

    def extract_snapshot():
        print("Extract snapshot")
        os.chdir(bitcoind_dir_path)
        tar = run(["tar", "xf", snapshot_path])
        print("Extracting done")
        if tar.returncode == 0:
            set_permissions(bitcoind_dir_path)

    def remove_snapshot():
        assert IOError("Corrupt snapshot file")
        if snapshot_path.is_file():
            print("Remove the utxoset-snapshot.* files to try again")
        #     # os.remove(snapshot_path)
        #
        # state_file = pathlib.Path(snapshot_path + ".st")
        # if state_file.is_file():
        #     pass
        #     # os.remove(snapshot_path + ".st")

    def compare_checksums():
        print("Comparing checksums")
        openssl_location = run(
            ["which", "openssl"], stdout=DEVNULL, stderr=DEVNULL
        )
        if openssl_location.returncode == 0:
            # openssl is installed
            openssl = run(
                ["openssl", "dgst", "-sha256", snapshot_path],
                stdout=PIPE,
                stderr=PIPE,
            )
            if openssl.returncode == 0:
                hash = str(bytes.decode(openssl.stdout))
                hash = hash.split(" ")[1].rstrip()

                if hash == checksum:
                    print("Checksums match")
                    return True
                print("Checksums do not match:")
                print("Expected: " + str(checksum))
                print("  Actual: " + str(hash))
                return False
            raise OSError(
                "Cannot compare hashes: " + bytes.decode(openssl.stderr)
            )
        else:
            shasum = run(
                ["sha256sum", snapshot_path], stdout=PIPE, stderr=PIPE
            )
            if shasum.returncode == 0:
                hash = shasum.stdout.split(" ")[0]
                print(hash)
                if hash == checksum:
                    print("Checksums match")
                    return True
                print("Checksums do not match: " + bytes.decode(shasum.stdout))
                return False
            raise OSError(
                "Cannot compare hashes: " + bytes.decode(shasum.stderr)
            )

    def download_snapshot():
        os.chdir(bitcoind_dir_path)
        print("Download snapshot")
        download = run(
            ["axel", "--quiet", "--no-clobber", url],
            stdout=PIPE,
            stderr=STDOUT,
        )
        if download.returncode == 0:
            if compare_checksums():
                extract_snapshot()
            else:
                remove_snapshot()
                download_snapshot()
        else:
            raise OSError("Download failed" + str(download.stdout))

    print("Checking existing filesystem structure")
    if bitcoind_dir_exists:
        print("Bitcoin directory exists")
        if snapshot_path.is_file():
            print("Snapshot archive exists")
            if pathlib.Path(bitcoind_dir / "blocks").is_dir():
                print("Bitcoin blocks directory exists, stopping")
                print("Remove the directory to fastsync")
                return
            if pathlib.Path(bitcoind_dir / "chainstate").is_dir():
                print("Bitcoin chainstate directory exists, stopping")
                print("Remove the directory to fastsync")
                return
            if compare_checksums():
                extract_snapshot()
            else:
                download_snapshot()
        else:
            download_snapshot()
    else:
        print("Bitcoin directory does not exist, creating")
        if pathlib.Path("/media/archive/archive").is_dir():
            pathlib.Path(bitcoind_dir).mkdir(exist_ok=True)
            download_snapshot()
        else:
            raise OSError(
                "Error: archive directory does not exist on your usb device"
            )


def create():
    """Create bitcoind directory structure and config file"""
    bitcoind_dir = pathlib.Path("/media/archive/archive/bitcoin")
    bitcoind_config = pathlib.Path("/home/lncm/bitcoin/bitcoin.conf")

    if bitcoind_dir.is_dir():
        print("bitcoind directory exists")
    else:
        print("bitcoind directory does not exist")
        bitcoind_dir.mkdir(exist_ok=True)

    if bitcoind_config.is_file():
        print("bitcoind bitcoin.conf exists")
    else:
        print("bitcoind bitcoin.conf does not exist, creating")
        shutil.copy(bitcoind_config, bitcoind_dir + "/bitcoin.conf")


def set_prune(prune_target, config_path=""):
    """Set bitcoind prune target, minimum 550"""
    if not config_path:
        config_path = cfg.BITCOIN_CONF
    set_ini_kv("prune", prune_target, config_path)


def set_rpcauth(bitcoin_conf=str(cfg.BITCOIN_CONF), invoicer_conf=str(cfg.INVOICER_CONF)):
    """Write rpcauth to bitcoind and invoicer configs"""
    auth_value, password = generate_rpcauth("lncm")

    try:
        rpcauth_val = get_ini_kv(bitcoin_conf, "rpcauth")
    except IOError:
        print("❌ Error: bitcoin config file not found")
        raise
    except KeyError:
        print("rpcauth unset")

    if rpcauth_val != '': 
        print("⚠️ Warning: not changing rpcauth, already set")
        return

    set_ini_kv("rpcauth", auth_value, bitcoin_conf)
    set_toml_kv(invoicer_conf, "user", "lncm", "bitcoind")
    set_toml_kv(invoicer_conf, "pass", password, "bitcoind")
    print("✅ set rpcauth successfully")
    return


def generate_rpcauth(username, password=""):
    """Generate bitcoind rpcauth string from username and optional password"""
    if not password:
        password = rpcauth.generate_password()
    salt = rpcauth.generate_salt(16)
    password_hmac = rpcauth.password_to_hmac(salt, password)
    auth_value = "{0}:{1}${2}".format(username, salt, password_hmac)
    return auth_value, password


def check():
    """Check bitcoind filesystem structure"""
    if not cfg.BITCOIN_PATH.is_dir():
        raise IOError("❌ bitcoin directory missing")
    print("✅ bitcoind directory exists")

    if not cfg.BITCOIN_CONF.is_file():
        raise IOError("❌ bitcoin config file is missing")
    print("✅ bitcoind config file exists")

    return True


class IniConfig(ConfigObj):
    """Allow ini-style ; comments"""
    COMMENT_MARKERS = ['#', ';']


def get_ini_kv(config_path, key, section=""):
    """
    Parse ini-style config files and print out values

    :param config_path: path to file
    :param key: left part of key value pair
    :param section: section of ini file
    :return: value of key
    """
    try:
        config = IniConfig(config_path, file_error=True, encoding='utf-8')
    except SyntaxError as error:
        print("⚠️ " + str(error))
    else:
        if section:
            if section in config:
                config = config[section]
                return config[key]
            print("❌ section '{s}' does not exist".format(s=section))
        if key in config:
            return config[key]
        print("❌ key '{k}' does not exist".format(k=key))


def set_ini_kv(key, value, config_path, section=""):
    """
    Set key to value in path
    kv pairs are separated by "="

    :param key: key to set
    :param value: value to set
    :param config_path: config file path
    :param section: config section
    """
    try:
        config = IniConfig(config_path, file_error=True, encoding='utf-8')
    except SyntaxError as error:
        print("⚠️ " + str(error))
    else:
        if section:
            config[section][key] = value
        else:
            config[key] = value
        config.write(delimiter='=')


def get_toml_kv(config_path, key, section=""):
    """get toml key value"""
    config = toml.load(config_path)
    if section:
        config = config[section]
    return config[key]


def set_toml_kv(config_path, key, value, section=""):
    """set toml key value"""
    config = toml.load(config_path)
    if section in config:
        config = config[section]
    config[key] = value
    with open(config_path, "w") as toml_file:
        toml.dump(config, toml_file)


if __name__ == "__main__":
    print("This file is not meant to be run directly")
