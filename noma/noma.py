#!/usr/bin/env python3
"""Noma [node management]

Usage:  noma start
        noma stop
        noma check
        noma logs
        noma info
        noma lnd create
        noma lnd backup
        noma lnd autounlock
        noma lnd autoconnect [<path>]
        noma lnd savepeers
        noma lnd connectapp
        noma lnd connectstring
        noma help [COMMAND]...
        noma (-h|--help)
        noma --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import os
from docopt import docopt
from noma import lnd
from noma import node


def _help(cmd):
    """
    Display help for a given command using docstrings.
    TODO:
    - figure out how to hide private functions
    - handle the discrepancy between `lnd create` and the called function
      (lnd.create()) properly... this probably means renaming
      lnd.create() to lnd.create()
    - get rid of the hacky if-then logic
    """
    if not cmd:
        help(node)
        return
    else:
        base = cmd[0]
        if base in dir(node):
            help(getattr(node, base))
            return
        elif len(cmd) > 1:
            cmd_2 = cmd[1]
            if base == "lnd":
                if cmd_2 == "create":
                    help(lnd.create)
                    return
                elif cmd_2 in dir(lnd):
                    help(getattr(lnd, cmd_2))
                    return
        elif base == "lnd":
            help(lnd)
            return
    print("Unknown help option: {}".format(cmd))


def lnd_fn(args):
    """
    lnd related functionality
    """
    if args["create"]:
        lnd.create()

    elif args["autounlock"]:
        lnd.autounlock()

    elif args["backup"]:
        lnd.backup()

    elif args["autoconnect"]:
        lnd.autoconnect(args["<path>"])

    elif args["savepeers"]:
        lnd.savepeers()

    elif args["connectstring"]:
        lnd.connectstring()


def node_fn(args):
    """
    node related functionality
    """
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

    elif args["help"]:
        _help(args["COMMAND"])


def main():
    """
    main noma entrypoint function
    """
    args = docopt(__doc__, version="Noma v0.5.1")

    if os.geteuid() == 0:
        if args["lnd"]:
            lnd_fn(args)
        else:
            node_fn(args)
    else:
        print("Sorry! You must be root")


if __name__ == "__main__":
    main()
