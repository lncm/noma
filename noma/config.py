"""
config.py defines configuration of filesystem structure

These constants are not to be changed during runtime

Pathlib objects represent PosixPaths
"""
from pathlib import Path

# These constants are not to be changed during runtime

"""LND Settings"""
LND_MODE = "neutrino"
LND_NET = "mainnet"

"""Filesystem"""
MEDIA_PATH = Path("/media")
NOMA_SOURCE = MEDIA_PATH / "noma"

COMPOSE_MODE_PATH = NOMA_PATH / "compose" / LND_MODE
NOMA_PATH = MEDIA_PATH / "noma"

"""Do not change below here"""
"""unless you know what you're doing"""

HOME_PATH = Path.home()

"""LND Paths"""
LND_CONF = LND_PATH / LND_MODE / "lnd.conf"
WALLET_PATH = LND_PATH / LND_MODE / "data" / "chain" / "bitcoin" / LND_NET / "wallet.db"
TLS_CERT_PATH = LND_PATH / LND_MODE / "tls.cert"
SEED_FILENAME = LND_PATH / "seed.txt"

# Save password control file (Add this file to save passwords)
SAVE_PASSWORD_CONTROL_FILE = LND_PATH / "save_password"

# Create password for writing
TEMP_PASSWORD_FILE_PATH = LND_PATH / "password.txt"

SESAME_PATH = LND_PATH / "sesame.txt"

"""LND Endpoints"""
# Generate seed
URL_GENSEED = "https://127.0.0.1:8080/v1/genseed"

# Initialize wallet
URL_INITWALLET = "https://127.0.0.1:8080/v1/initwallet"
URL_UNLOCKWALLET = "https://127.0.0.1:8080/v1/unlockwallet"
