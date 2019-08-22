#!/usr/bin/env python3
"""noma [node management]

Usage:
  noma start
  noma stop
  noma check
  noma logs
  noma info
  noma lnd create
  noma lnd backup
  noma lnd autounlock
  noma lnd autoconnect [<path>]
  noma lnd savepeers
  noma (-h|--help)
  noma --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import os
from docopt import docopt
from noma import node


def lnd(args):
    from noma import lnd

    if args["create"]:
        lnd.check_wallet()

    elif args["autounlock"]:
        lnd.autounlock()

    elif args["backup"]:
        lnd.backup()

    elif args["autoconnect"]:
        lnd.autoconnect(args["<path>"])

    elif args["savepeers"]:
        lnd.savepeers()


def node(args):
    from noma import node

    if args["info"]:
        node.info()

    elif args["start"]:
        node.start()

    elif args["stop"]:
        node.stop()

    elif args["logs"]:
        node.logs()

    elif args["check"]:
        node.check()


def main():
    args = docopt(__doc__, version="v0.5.0")

    if os.geteuid() == 0:
        if args["lnd"]:
            lnd(args)
        else:
            node(args)
    else:
        print("Sorry! You must be root")


if __name__ == "__main__":
    main()
