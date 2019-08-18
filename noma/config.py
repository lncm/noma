"""
config.py defines configuration of filesystem structure

Pathlib objects represent PosixPaths which are exported
in config_obj.py as dot notation under cfg.*
"""
from pathlib import Path

# These constants are not to be changed during runtime
MEDIA_PATH = Path("/media")

NOMA_PATH = MEDIA_PATH / "noma"
COMPOSE_MODE_PATH = NOMA_PATH / "compose" / "neutrino"

LND_PATH = NOMA_PATH / "lnd"
BITCOIND_PATH = NOMA_PATH / "bitcoind"

HOME_PATH = Path.home()