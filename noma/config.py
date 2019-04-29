from pathlib import Path

HOME_DIR = Path("/home/lncm")
MEDIA_DIR = Path("/media")
# host = [HOME_DIR, MEDIA_DIR]

ARCHIVE_DIR = MEDIA_DIR / "archive" / "archive"
VOLATILE_DIR = MEDIA_DIR / "volatile" / "volatile"
IMPORTANT_DIR = MEDIA_DIR / "important" / "important"
FACTORY_DIR = HOME_DIR / "pi-factory"
COMPOSE_DIR = HOME_DIR / "compose"
NOMA_DIR = HOME_DIR / "noma"
# node = [ARCHIVE_DIR, VOLATILE_DIR, IMPORTANT_DIR, FACTORY_DIR, COMPOSE_DIR, NOMA_DIR]

SNAPSHOT_WEBROOT = "http://utxosets.blob.core.windows.net/public/"
SNAPSHOT_NAME = "utxo-snapshot-bitcoin-mainnet-565305.tar"
SNAPSHOT_URL = SNAPSHOT_WEBROOT + SNAPSHOT_NAME
# snapshot = [SNAPSHOT_WEBROOT, SNAPSHOT_NAME]

BITCOIN_DIR = MEDIA_DIR / "archive" / "archive" / "bitcoin"
BITCOIND_CONFIG = BITCOIN_DIR / "bitcoin.conf"

# bitcoind = [BITCOIN_DIR, SNAPSHOT_URL]

LND_DIR = MEDIA_DIR / "important" / "important" / "lnd"
# lnd = [LND_DIR]

# invoicer = {}

# nginx = {}

# tor = {}

# def main():
#     settings = [
#         host,
#         node,
#         compose,
#         snapshot,
#         bitcoind,
#         lnd,
#         invoicer,
#         nginx,
#         tor,
#     ]
#     return settings
#
#
# main()
