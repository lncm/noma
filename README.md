# noma
noma - node management

```
Usage:
  noma (info|start|stop|restart|logs|check|status)
  noma (temp|swap|ram)
  noma (freq|memory|voltage) [<device>]
  noma usb-setup
  noma tunnel <port> <host>
  noma (backup|restore|source|diff|devtools)
  noma reinstall [--full]
  noma bitcoind (start|stop|info|fastsync|status|check)
  noma bitcoind get <key>
  noma bitcoind set <key> <value>
  noma bitcoind logs [--tail]
  noma lnd (start|stop|info)
  noma lnd logs [--tail]
  noma lnd connect <address>
  noma lnd (create|unlock|status|check)
  noma lnd lncli [<command>...]
  noma lnd get <key> [<section>] [<path>]
  noma lnd set <key> <value> [<section>] [<path>]
  noma lnd autounlock
  noma lnd autoconnect [<path>]
  noma (-h|--help)
  noma --version

Options:
  -h --help     Show this screen.
  --version     Show version.
```

### build instructions

1. `python3 setup.py bdist_wheel`
2. `pip install dist/noma-0.1-py3-none-any.whl`
