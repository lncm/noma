"""
config.py defines configuration of filesystem structure

These constants are not to be changed during runtime

Pathlib objects represent PosixPaths
"""
from pathlib import Path

"""LND Settings"""
LND_MODE = "neutrino"
LND_NET = "mainnet"

"""Filesystem"""
MEDIA_PATH = Path("/media")
NOMA_SOURCE = MEDIA_PATH / "noma"

"""Remote SSH backup host"""
SSH_PORT = "22"
# Make sure to use a passphrase-less private key
SSH_IDENTITY = "~/.ssh/id_ed25519"
# [user@]host:[path]
SSH_TARGET = "user@ssh-hostname:/path/to/backup/dir/"

"""Do not change below here"""
"""unless you know what you're doing"""

HOME_PATH = Path.home()
COMPOSE_MODE_PATH = NOMA_SOURCE / "compose" / LND_MODE

"""LND Paths"""
LND_PATH = NOMA_SOURCE / "lnd" / LND_MODE
LND_CONF = LND_PATH / "lnd.conf"
CHAIN_PATH = LND_PATH / "data" / "chain" / "bitcoin"
WALLET_PATH = CHAIN_PATH / LND_NET / "wallet.db"
TLS_CERT_PATH = LND_PATH / "tls.cert"

MACAROON_PATH = CHAIN_PATH / LND_NET / "admin.macaroon"
SEED_FILENAME = LND_PATH / "seed.txt"
CHANNEL_BACKUP = CHAIN_PATH / LND_NET / "channel.backup"

"""LND Create Password"""
# Save password control file (Add this file to save passwords)
SAVE_PASSWORD_CONTROL_FILE = LND_PATH / "save_password"
# Create password for writing
PASSWORD_FILE_PATH = LND_PATH / "password.txt"

"""LND Endpoints"""
URL_GRPC = "192.168.83.33:10009"
# Generate seed
URL_GENSEED = "https://127.0.0.1:8080/v1/genseed"
# Initialize wallet
URL_INITWALLET = "https://127.0.0.1:8080/v1/initwallet"
URL_UNLOCKWALLET = "https://127.0.0.1:8080/v1/unlockwallet"
