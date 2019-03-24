import os
import shutil
from subprocess import call
import psutil
import pathlib
import time


def get_swap():
    """Get swap"""
    return round(psutil.swap_memory().total / 1048576)


def get_ram():
    """Get RAM"""
    return round(psutil.virtual_memory().total / 1048576)


def check():
    """check box filesystem structure"""
    archive_path = pathlib.Path("/media/archive/archive")
    important_path = pathlib.Path("/media/important/important")
    volatile_path = pathlib.Path("/media/volatile/volatile")

    archive_exists = archive_path.is_dir()
    important_exists = important_path.is_dir()
    volatile_exists = volatile_path.is_dir()

    if archive_exists:
        print("archive usb device exists")
    else:
        print("archive usb device is missing")

    if important_exists:
        print("important usb device exists")
    else:
        print("important usb device is missing")

    if volatile_exists:
        print("volatile usb device exists")
    else:
        print("volatile usb device is missing")

    if archive_exists and important_exists and volatile_exists:
        return True
    return False


def start():
    """Start default docker compose"""
    os.chdir("/home/lncm/compose")
    call(["docker-compose", "up", "-d"])


def backup():
    """Backup apkovl to important usb device"""
    call(["lbu", "pkg", "-v", "/media/important/important/"])


def devtools():
    """Install common development tools, nano, tmux, git, etc"""
    call(["apk", "update"])
    call(["apk", "add", "tmux", "sudo", "git", "rsync", "htop", "iotop", "nmap", "nano"])


def is_running(node=''):
    """Check if container is running

    :return bool: container is running"""
    from docker import from_env

    if not node:
        node = 'bitcoind'
    docker_host = from_env()
    compose_name = "compose_%s_1" % node
    for container in docker_host.containers.list():
        if compose_name in container.name:
            return True
    return False


def stop_daemons():
    """Check and wait for clean shutdown of both bitcoind and lnd"""
    if not is_running("bitcoind") and not is_running("lnd"):
        return print("bitcoind and lnd are already stopped")

    for i in range(5):
            if not is_running("bitcoind") and not is_running("lnd"):
                break
            if is_running("bitcoind"):
                # stop bitcoind
                call(["docker", "exec", "compose_bitcoind_1", "bitcoin-cli", "stop"])
            if is_running("lnd"):
                # stop lnd
                call(["docker", "exec", "compose_lnd_1", "lncli", "stop"])

            time.sleep(2)
            i -= 1

    for i in range(5):
        import docker
        client = docker.from_env()

        if not is_running("bitcoind") and not is_running("lnd"):
            break

        for container in client.containers.list():
            if container.name == "bitcoind" or "lnd":
                container.stop()
                time.sleep(2)
                i -= 1


def voltage(device=""):
    """
    Get chip voltage (default: core)

    :param device: core, sdram_c, sdram_i, sdram_p
    :return str: voltage
    """
    if not device:
        device = 'core'
    call(["/opt/vc/bin/vcgencmd", "measure_volts", device])


def temp():
    """
    Get CPU temperature

    :return str: CPU temperature
    """
    cpu_temp_path = "/sys/class/thermal/thermal_zone0/temp"
    with open(cpu_temp_path, 'r') as file:
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


def logs(node=''):
    """Show logs of node specified, defaults to bitcoind

    return str: tailling logs"""
    if node:
        container_name = "compose_" + node + "_1"
        call(["docker", "logs", "-f", container_name])
    else:
        # default to bitcoind if node not given
        call(["docker", "logs", "-f", "compose_bitcoind_1"])


def install_git():
    """Install git"""
    if shutil.which("git"):
        pass
    else:
        call(["apk", "update"])
        call(["apk", "add", "git"])


def get_source():
    """Get latest pi-factory source code or update"""
    install_git()

    factory_path = pathlib.Path("/home/lncm/pi-factory")
    if factory_path.is_dir():
        print("source directory already exists")
        print("going to update with git pull")
        os.chdir("/home/lncm/pi-factory")
        call(["git", "pull"])
    else:
        os.chdir("/home/lncm")
        call(["git", "clone", "https://github.com/lncm/pi-factory.git"])


def tunnel(port, host):
    """Keep the SSH tunnel open, no matter what"""
    while True:
        try:
            print("Tunneling local port 22 to " + host + ":" + port)
            port_str = "-R " + port + ":localhost:22"
            call(["autossh", "-M 0", "-o ServerAliveInterval=60", "-o ServerAliveCountMax=10", port_str, host])
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

    os.chdir("/home/lncm/pi-factory")
    call(["git", "pull"])
    print("Migrating current WiFi credentials")
    supplicant_sd = pathlib.Path("/etc/wpa_supplicant/wpa_supplicant.conf")
    supplicant_gh = pathlib.Path("etc/wpa_supplicant/wpa_supplicant.conf")
    shutil.copy(supplicant_sd, supplicant_gh, )
    call(["./make_apkovl.sh"])
    call(["mount", "-o", "remount,ro", "/dev/mmcblk0p1", "/media/mmcblk0p1"])
    shutil.copy("box.apkovl.tar.gz", "/media/mmcbkl0p1")
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
    os.chdir("/home/lncm/pi-factory")
    call(["git", "pull"])
    call(["make_upgrade.sh"])


def do_diff():
    """Diff current system configuration state with original git repository"""
    install_git()

    factory = pathlib.Path("/home/lncm/pi-factory")

    def make_diff():
        print("Generating /home/lncm/etc.diff")
        call(["diff", "-r", "etc", "/home/lncm/pi-factory/etc"])
        print("Generating /home/lncm/usr.diff")
        call(["diff", "-r", "usr", "/home/lncm/pi-factory/usr"])
        print("Generating /home/lncm/home.diff")
        call(["diff", "-r", "home", "/home/lncm/pi-factory/home"])

    if factory.is_dir():
        os.chdir("/home/lncm/pi-factory")
        print("Getting latest sources")
        call(["git", "pull"])
        make_diff()
    else:
        get_source()
        make_diff()


if __name__ == "__main__":
    print("This file is not meant to be run directly")
