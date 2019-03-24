.. noma documentation master file, created by
   sphinx-quickstart on Sun Mar 24 11:00:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Noma documentation
================================

Command-line Usage:
###################

**node**::

  noma (info|start|stop|restart|logs|check|status)
  noma (temp|swap|ram)
  noma (freq|memory|voltage) [<device>]
  noma usb-setup
  noma tunnel <port> <host>
  noma (backup|restore|source|diff|devtools)
  noma reinstall [--full]

**bitcoind**::

  noma bitcoind (start|stop|info|fastsync|status|check)
  noma bitcoind get <key>
  noma bitcoind set <key> <value>
  noma bitcoind logs [--tail]

**lnd**::

  noma lnd (start|stop|info)
  noma lnd logs [--tail]
  noma lnd connect <address>
  noma lnd (create|unlock|status|check)
  noma lnd lncli [<command>...]
  noma lnd get <key> [<section>] [<path>]
  noma lnd set <key> <value> [<section>] [<path>]
  noma lnd autounlock
  noma lnd autoconnect [<path>]

**noma**::

  noma (-h|--help)
  noma --version

   Options:
  -h --help     Show this screen.
  --version     Show version.


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. automodule:: noma.node
   :members:

.. automodule:: noma.bitcoind
   :members:

.. automodule:: noma.lnd
   :members:

.. automodule:: noma.install
   :members:

.. automodule:: noma.usb
   :members:

.. automodule:: noma.rpcauth
   :members:

