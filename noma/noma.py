#!/usr/bin/env python3
"""noma [node management]

Usage:
  noma start
  noma stop
  noma check
  noma logs
  noma lnd info
  noma lnd create
  noma lnd backup
  noma lnd restore
  noma lnd autounlock
  noma lnd autoconnect [<path>]
  noma lnd savepeers
  noma (-h|--help)
  noma --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt


# def bitcoind(args):
#     from noma import node
#     from noma import bitcoind
#     from subprocess import call
#
#     if args["start"]:
#         bitcoind.start()
#
#     elif args["stop"]:
#         bitcoind.stop()
#
#     elif args["logs"]:
#         if args["--tail"]:
#             call(["tail", "-f", "/media/volatile/volatile/bitcoin/debug.log"])
#         else:
#             if alt_log_path.is_file():
#                 call(["tail", "-f", alt_log_path])
#             else:
#                 node.logs("bitcoind")
#
#     elif args["info"]:
#         call(
#             ["docker", "exec", "compose_bitcoind_1", "bitcoin-cli", "-getinfo"]
#         )
#
#     elif args["fastsync"]:
#         bitcoind.fastsync()
#
#     elif args["check"]:
#         bitcoind.check()
#
#     elif args["status"]:
#         if node.is_running("bitcoind"):
#             print("bitcoind is running")
#         else:
#             print("bitcoind is not running")
#
#     elif args["set"]:
#         bitcoind.set_kv(
#             args["<first>"],
#             args["<second>"],
#             "/media/archive/archive/bitcoin_big/bitcoin.conf",
#         )
#
#     elif args["get"]:
#         bitcoind.get_kv(
#             args["<first>"], "/media/archive/archive/bitcoin_big/bitcoin.conf"
#         )
#
#     elif args["rpcauth"]:
#         bitcoind.generate_rpcauth(args["<username>"], args["<password>"])


def lnd(args):
    from noma import lnd
    from noma import node
    from subprocess import call

    if args["start"]:
        if node.is_running("lnd"):
            print("lnd is already running")
        else:
            call(["docker", "start", "compose_lnd_1"])

    elif args["stop"]:
        if node.is_running("lnd"):
            call(["docker", "exec", "compose_lnd_1", "lncli", "stop"])
        else:
            print("lnd is already stopped")

    elif args["connect"]:
        print(
            call(
                [
                    "docker",
                    "exec",
                    "compose_lnd_1",
                    "lncli",
                    "connect",
                    args["<address>"],
                ]
            )
        )

    elif args["autoconnect"]:
        lnd.autoconnect(args["<path>"])

    elif args["lncli"]:
        call(["docker", "exec", "compose_lnd_1", "lncli", args["<command>"]])

    elif args["logs"]:
        if args["--tail"]:
            call(
                [
                    "tail",
                    "-f",
                    "/media/volatile/volatile/lnd/logs/bitcoin/mainnet/lnd.log",
                ]
            )
        else:
            node.logs("lnd")

    elif args["info"]:
        call(["docker", "exec", "compose_lnd_1", "lncli", "getinfo"])

    elif args["create"]:
        lnd.check_wallet()

    elif args["unlock"]:
        # manually unlock lnd wallet
        call(["docker", "exec", "-it", "compose_lnd_1", "lncli", "unlock"])

    elif args["autounlock"]:
        lnd.autounlock()

    elif args["status"]:
        if node.is_running("lnd"):
            print("lnd is running")
        else:
            print("lnd is not running")

    elif args["check"]:
        lnd.check()

    elif args["set"]:
        lnd.set_kv(
            args["<key>"], args["<value>"], args["<section>"], args["<path>"]
        )

    elif args["get"]:
        print(lnd.get_kv(args["<key>"], args["<section>"], args["<path>"]))


def node(args):
    from noma import node
    from subprocess import call

    if args["info"]:
        call(
            ["docker", "exec", "compose_bitcoind_1", "bitcoin-cli", "-getinfo"]
        )
        call(["docker", "exec", "compose_lnd_1", "lncli", "getinfo"])

    elif args["start"]:
        if node.is_running("bitcoind"):
            print("bitcoind is already running")
        if node.is_running("lnd"):
            print("lnd is already running")
        node.start()

    elif args["stop"]:
        node.stop_daemons()
        # now we can safely stop
        call(["service", "docker-compose", "stop"])

    # elif args["restart"]:
    #     node.stop_daemons()
    #     # now we can safely restart
    #     call(["service", "docker-compose", "restart"])

    elif args["logs"]:
        node.logs()

    elif args["temp"]:
        print(node.temp())

    elif args["voltage"]:
        node.voltage(args["<device>"])

    elif args["freq"]:
        node.freq(args["<device>"])

    elif args['turbo']:
        print("Set CPU scaling")
        from subprocess import DEVNULL
        for cpu_num in range(0, 4):
            device_path = "/sys/devices/system/cpu/cpu{n}/cpufreq/scaling_governor".format(n=cpu_num)
            call(["echo", "ondemand > {p} ".format(p=device_path)], shell=True, stdout=DEVNULL, stderr=DEVNULL)

    elif args['memory']:
        print(node.memory(args['<device>']))

    elif args["backup"]:
        node.backup()

    elif args["restore"]:
        print("restore unimplemented")

    elif args["source"]:
        node.install_git()
        node.get_source()

    elif args["diff"]:
        node.do_diff()

    elif args["reinstall"]:
        print("Warning: this will wipe data on your SD card!")
        if args["--confirm"]:
            if args["--full"]:
                node.full_reinstall()
            else:
                node.reinstall()
        else:
            print("You must pass --confirm to continue")

    elif args["tunnel"]:
        node.tunnel(args["<port>"], args["<host>"])

    elif args["usb-setup"]:
        import noma.install

        noma.install.usb_setup()

    elif args["install-box"]:
        import noma.install

        noma.install.install_box()

    elif args["create-swap"]:
        from noma import install
        print(install.create_swap())

    elif args["check"]:
        node.check()

    elif args["devtools"]:
        node.devtools()

    elif args["status"]:
        if node.is_running("bitcoind"):
            print("bitcoind is running")
        else:
            print("bitcoind is not running")
        if node.is_running("lnd"):
            print("lnd is running")
        else:
            print("lnd is not running")

    elif args["swap"]:
        node.get_swap()

    elif args["ram"]:
        node.get_ram()


def main():
    args = docopt(__doc__, version="v0.4.3")

    # if args["bitcoind"]:
    #     bitcoind(args)
    if args["lnd"]:
        lnd(args)
    else:
        node(args)


if __name__ == "__main__":
    main()
