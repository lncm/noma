# Noma - lightning node management

CLI utility and Python API to manage bitcoin lightning nodes.


[![Documentation Status](https://readthedocs.org/projects/noma/badge/?version=latest)](https://noma.readthedocs.io/en/latest/?badge=latest)

### Command-line usage:

**node**:
```
noma (info|start|stop|restart|logs|check|status)
noma (temp|swap|ram)
noma (freq|memory|voltage) [<device>]
noma usb-setup
noma tunnel <port> <host>
noma (backup|restore|source|diff|devtools)
noma reinstall [--full]
```

**bitcoind**:
```
noma bitcoind (start|stop|info|fastsync|status|check)
noma bitcoind get <key>
noma bitcoind set <key> <value>
noma bitcoind logs [--tail]
```

**lnd**:
```
noma lnd (start|stop|info)
noma lnd logs [--tail]
noma lnd connect <address>
noma lnd (create|unlock|status|check)
noma lnd lncli [<command>...]
noma lnd get <key> [<section>] [<path>]
noma lnd set <key> <value> [<section>] [<path>]
noma lnd autounlock
noma lnd autoconnect [<path>]
```

**noma**:
```
noma (-h|--help)
noma --version

 Options:
-h --help     Show this screen.
--version     Show version.
```

### API documentation
[Read the Docs](https://noma.readthedocs.io/en/latest/)


### Dependencies
To get the most out of this tool we highly recommend to have `docker` and `docker-compose` installed.

Currently, some third-party components needs to be installed and configured separately when not using `noma` in combination with https://github.com/lncm/pi-factory to enable all functionality.

Some `noma` functions are specific to Raspberry Pi hardware.


### Pre-build Instructions

#### Alpine Linux

* ```apk add gcc```
* ```apk add python-dev```

### Build instructions
0. `pip3 install wheel docker docker-compose`
1. `python3 setup.py bdist_wheel`
2. `pip install dist/noma-0.2.1-py3-none-any.whl`

### Build docs
0. `pip3 install sphinx sphinx-rtd-theme`
1. `cd docs`
2. `make html`
docs can be found at `docs/_build/html/index.html`
