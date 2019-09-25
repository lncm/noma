#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Node hardware and software management related functionality
"""
import os
import shutil
from subprocess import call
import pathlib
import time
import psutil
import noma.config as cfg
import noma.lnd


def get_swap():
    """Return amount of swap"""
    return round(psutil.swap_memory().total / 1048576)


def get_ram():
    """Return amount of RAM"""
    return round(psutil.virtual_memory().total / 1048576)


def check():
    """check box filesystem structure"""
    # TODO: only print when logging is enabled

    media_exists = bool(cfg.MEDIA_PATH.is_dir())
    noma_exists = bool(cfg.NOMA_SOURCE.is_dir())
    compose_exists = bool(cfg.COMPOSE_MODE_PATH.is_dir())

    dir_exists_text = str(" directory exists")
    dir_missing_text = str(" directory is missing or inaccessible")

    if media_exists:
        print("✅ " + "Media" + dir_exists_text)
    else:
        print("❌ " + "Media" + dir_missing_text)

    if noma_exists:
        print("✅ " + "Noma" + dir_exists_text)
    else:
        print("❌ " + "Noma" + dir_missing_text)

    if compose_exists:
        print("✅ " + "Compose" + dir_exists_text)
    else:
        print("❌ " + "Compose" + dir_missing_text)

    if media_exists and noma_exists and compose_exists:
        return True
    return False


def start():
    """Start default docker compose"""
    if is_running("lnd"):
        print("lnd is already running")
        exit(1)
    if not check() and not noma.lnd.check():
        print("Fetching compose from noma repo")
        get_source()

    os.chdir(cfg.COMPOSE_MODE_PATH)
    call(["docker-compose", "up", "-d"])


def info():
    # Show dashboard with aggregated information
    if is_running("lnd"):
        print("lnd is running")
        call(["docker", "exec", cfg.LND_MODE + "_lnd_1", "lncli", "getinfo"])
    else:
        print("lnd is not running")


def devtools():
    """Install common development tools, nano, tmux, git, etc"""
    call(["apk", "update"])
    call(
        [
            "apk",
            "add",
            "tmux",
            "sudo",
            "git",
            "rsync",
            "htop",
            "iotop",
            "nmap",
            "nano",
        ]
    )


def is_running(node=""):
    """Check if container is running

    :return bool: container is running"""
    from docker import from_env
    import requests

    if not node:
        node = "lnd"
    docker_host = from_env()
    compose_name = cfg.LND_MODE + "_" + node + "_1"
    try:
        for container in docker_host.containers.list():
            if compose_name in container.name:
                return True
    except AttributeError:
        return None
    except ConnectionError:
        return None
    except requests.exceptions.ConnectionError:
        return None

    return False


def stop(timeout=1, retries=5):
    """Check and wait for clean shutdown of lnd"""

    def clean_stop():
        # ensure clean shutdown of lnd
        print("lnd is running, stopping with lncli stop")
        success = call(["docker", "exec", cfg.LND_MODE + "_lnd_1", "lncli", "stop"])
        if success == 0:
            print("✅ lncli stop returned success")
        else:
            print("❌ lncli stop failed")

        print("waiting " + str(timeout) + "s for lnd to stop...")
        time.sleep(timeout)

    for tries in range(retries):
        if is_running("lnd"):
            clean_stop()
            retries -= 1
        else:
            print("✅ lnd is stopped")
            exit(0)

    print("❌ Failed to stop lnd")


def voltage(device=""):
    """
    Get chip voltage (default: core)

    :param device: core, sdram_c, sdram_i, sdram_p
    :return str: voltage
    """
    if not device:
        device = "core"
    call(["/opt/vc/bin/vcgencmd", "measure_volts", device])


def temp():
    """
    Get CPU temperature

    :return str: CPU temperature
    """
    cpu_temp_path = "/sys/class/thermal/thermal_zone0/temp"
    with open(cpu_temp_path, "r") as file:
        cpu_temp = file.read()
    return str(int(cpu_temp) / 1000) + "C"


def freq(device=""):
    """
    Get chip clock (default: arm)

    :device str: arm, core, h264, isp, v3d, uart, pwm, emmc, pixel, vec, hdmi, dpi
    :return str: chip frequency
    """
    if device:
        call(["/opt/vc/bin/vcgencmd", "measure_clock", device])
    else:
        call(["/opt/vc/bin/vcgencmd", "measure_clock", "arm"])


def memory(device=""):
    """
    Get memory allocation split between cpu and gpu

    :param str device: arm, gpu
    :return str: memory allocated
    """
    if device:
        call(["/opt/vc/bin/vcgencmd", "get_mem", device])
        call(["/opt/vc/bin/vcgencmd", "get_mem", "arm"])


def logs(node=""):
    """Tail logs of node specified, defaults to lnd"""
    if node:
        container_name = cfg.LND_MODE + "_" + node + "_1"
        call(["docker", "logs", "-f", container_name])
    else:
        # default to lnd if node not given
        call(["docker", "logs", "-f", cfg.LND_MODE + "_lnd_1"])


def install_git():
    """Install git"""
    if shutil.which("git"):
        pass
    else:
        call(["apk", "update"])
        call(["apk", "add", "git"])


def get_source():
    """Get latest noma source code or update"""
    install_git()

    if cfg.NOMA_SOURCE.is_dir():
        print("Source directory already exists")
        print("Going to attempt update with git pull")
        os.chdir(cfg.NOMA_SOURCE)
        call(["git", "pull"])
    else:
        # source does not exist
        call(
            [
                "git",
                "clone",
                "https://github.com/lncm/noma.git",
                cfg.NOMA_SOURCE,
            ]
        )


def tunnel(port, hostname):
    """Keep the SSH tunnel open, no matter what"""
    while True:
        try:
            print("Tunneling local port 22 to " + hostname + ":" + port)
            port_str = "-R " + port + ":localhost:22"
            call(
                [
                    "autossh",
                    "-M 0",
                    "-o ServerAliveInterval=60",
                    "-o ServerAliveCountMax=10",
                    port_str,
                    hostname,
                ]
            )
        except Exception as error:
            print(error)


def reinstall():
    """
    Regenerate box.apkovl.tar.gz and mark SD as uninstalled

    Leaves FAT partition alone. kernel, kernel modules,
    containers, etc on the boot partition remain the same

    Since there is less to download this method is faster
    than reinstall --full
    """
    install_git()
    get_source()

    os.chdir(cfg.NOMA_SOURCE)
    call(["git", "pull"])
    print("Migrating current WiFi credentials")
    supplicant_sd = pathlib.Path("/etc/wpa_supplicant/wpa_supplicant.conf")
    supplicant_gh = pathlib.Path("etc/wpa_supplicant/wpa_supplicant.conf")
    shutil.copy(supplicant_sd, supplicant_gh)
    call(["./make_apkovl.sh"])
    call(["mount", "-o", "remount,ro", "/dev/mmcblk0p1", "/media/mmcblk0p1"])
    shutil.copy("box.apkovl.tar.gz", "/media/mmcbkl0p1/")
    os.remove("/media/mmcblk0p1/installed")
    call(["mount", "-o", "remount,ro", "/dev/mmcblk0p1", "/media/mmcblk0p1"])
    print("Done")
    print("Please reboot to upgrade your box")


def full_reinstall():
    """
    Full reinstall replaces entire FAT contents (boot partition),
    and the ext4 data contents as if we installed from freshly burned SD card
    """
    print("Starting upgrade...")
    install_git()
    get_source()
    os.chdir(cfg.NOMA_SOURCE)
    call(["git", "pull"])
    call(["make_upgrade.sh"])


def do_diff():
    """Diff current system configuration state with original git repository"""
    install_git()

    def make_diff():

        print("Generating {h}/noma.diff".format(h=cfg.HOME_PATH))
        call(["diff", "-r", "/media/noma", "{h}/noma".format(h=cfg.HOME_PATH)])

    if cfg.NOMA_SOURCE.is_dir():
        os.chdir(cfg.NOMA_SOURCE)
        print("Getting latest sources")
        call(["git", "pull"])
        make_diff()
    else:
        get_source()
        make_diff()


if __name__ == "__main__":
    print("This file is not meant to be run directly")
