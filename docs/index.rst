.. noma documentation master file, created by
   sphinx-quickstart on Sun Mar 24 11:00:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 4
   :caption: Contents:

Noma
==================
CLI utility and Python API to manage bitcoin lightning nodes.

Command-line Usage
==================
.. automodule:: noma.noma

API Modules
===========

node
----
.. automodule:: noma.node
   :members: start, stop, check, logs, info

lnd
---
.. automodule:: noma.lnd
   :members: create, backup, autounlock, autoconnect, savepeers, connectapp, connectstring

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
