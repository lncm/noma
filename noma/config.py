"""
config.py defines configuration of filesystem structure

Pathlib objects represent PosixPaths and are exported as a
dir object within noma.config
"""
from pathlib import Path

# These constants are not to be changed during runtime
MEDIA_PATH = Path("/media")

NOMA_PATH = MEDIA_PATH / "noma"
COMPOSE_MODE_PATH = NOMA_PATH / "compose" / "neutrino"

LND_PATH = NOMA_PATH / "lnd"
BITCOIND_PATH = NOMA_PATH / "bitcoind"

HOME_PATH = Path.home()

dirs = {'media': MEDIA_PATH,
        'noma': NOMA_PATH,
        'compose': COMPOSE_MODE_PATH,
        'lnd': LND_PATH,
        'bitcoind': BITCOIND_PATH,
        'home': HOME_PATH}