"""
Node installation related functionality
"""
from pathlib import Path
import shutil
from subprocess import run, call, Popen, PIPE, DEVNULL, STDOUT
from time import sleep
from noma import usb
import requests


def create_dir(path):
    Path(path).mkdir(exist_ok=True)
    if Path(path).is_dir():
        return True
    return False


def check_installed(installed="/media/mmcblk0p1/installed"):
    """Check if LNCM-Box is installed"""
    if Path(installed).is_file():
        with open(installed, "r") as file:
            lines = file.readlines()
            for line in lines:
                print(line)
        return True
    return False


def move_cache(cache_dir="/media/mmcblk0p1/cache", var_cache="/var/cache/apk"):
    """Let apk cache live on persistent volume"""
    print("Let apk cache live on persistent volume")
    if Path(cache_dir).is_dir():
        print("Removing {v}".format(v=var_cache))
        shutil.rmtree(var_cache)

        print("Copy {v} to {c}".format(v=var_cache, c=cache_dir))
        shutil.copytree(cache_dir, var_cache)

        print("Running setup-apkcache")
        setup = run(["setup-apkcache", var_cache], stdout=PIPE, stderr=STDOUT)
        if setup.returncode == 0:
            print("setup-apkcache was successful")
        else:
            raise OSError(
                "setup-apkcache was not successful \n" + setup.stdout
            )
        return setup.returncode


def enable_swap():
    """Enable swap at boot"""
    print("Enable swap at boot")
    add_boot = run(["rc-update", "add", "swap", "boot"])
    add_default = run(["rc-update", "add", "swap", "default"])
    if add_boot.returncode == 0 and add_default.returncode == 0:
        return True
    return False


def install_firmware():
    """Install raspberry-pi firmware"""
    print("Install raspberry-pi firmware")
    call(["apk", "add", "raspberrypi"])


def apk_update():
    """Update apk mirror repositories"""
    print("Update package repository")
    call(["apk", "update"])


def install_apk_deps():
    """Install misc dependencies"""
    print("Install dependencies")
    call(["apk", "add", "curl", "jq", "autossh", "axel"])


def mnt_ext4(device, path):
    """Mount device at path using ext4"""
    exitcode = call(
        ["mount", "-t ext4", "/dev/" + device, path],
        stdout=DEVNULL,
        stdin=DEVNULL,
    )
    return exitcode


def mnt_any(device, path):
    """Mount device at path using any filesystem"""
    exitcode = call(
        ["mount", "/dev/" + device, path], stdout=DEVNULL, stdin=DEVNULL
    )
    return exitcode


def setup_nginx():
    """Setup nginx paths and config files"""
    nginx_volatile = Path("/media/volatile/volatile/nginx/").is_dir()
    if nginx_volatile:
        print("Nginx volatile directory found")
    else:
        print("Creating nginx volatile directory")
        Path("/media/volatile/volatile/nginx").mkdir(exist_ok=True)
    nginx_important = Path("/media/important/important/nginx").is_dir()
    if nginx_important:
        print("Nginx important directory found")
    else:
        print("Copying nginx config to important media")
        destination = Path("/media/important/important/nginx")
        origin = Path("/etc/nginx")
        shutil.copytree(origin, destination)


def check_for_destruction(device, path):
    """Check devices for destruction flag. If so, format with ext4"""
    print("Check devices for destruction flag")
    destroy = Path(path + "/DESTROY_ALL_DATA_ON_THIS_DEVICE/").is_dir()
    if destroy:
        print("Destruction flag found!")
        print(
            "Going to destroy all data on /dev/{} in 3 seconds...".format(
                device
            )
        )
        sleep(3)
        unmounted = call(["umount", "/dev/" + device])
        if unmounted and not usb.is_mounted(device):
            print("Going to format {d} with ext4 now".format(d=device))
            call(["mkfs.ext4", "-F", "/dev/" + device])
            if mnt_ext4(device, path) == 0 and usb.is_mounted(device):
                print(
                    "{d} formatted with ext4 successfully and mounted.".format(
                        d=device
                    )
                )
                return True
        else:
            unmounted = call(["umount", "-f", "/dev/" + device])

            if unmounted and not usb.is_mounted(device):
                print("Going to format {d} with ext4 now".format(d=device))
                call(["mkfs.ext4", "-F", "/dev/" + device])
                mounted = mnt_ext4(device, path)

                if mounted == 0 and usb.is_mounted(device):
                    print(
                        "{d} formatted with ext4 successfully and mounted.".format(
                            d=device
                        )
                    )
                    return True
            else:
                print("Error mounting {}".format(device))
                return False
    else:
        print("{} is not flagged for being wiped".format(device))
        return True


def fallback_mount(partition, path):
    """Attempt to mount partition at path using ext4 first and falling back to any

    :return bool: success
    """
    print("Mount ext4 storage device: {}".format(partition))

    if usb.is_mounted(partition):
        return True

    if mnt_ext4(partition, path) == 0 and usb.is_mounted(partition):
        print("{d} is mounted as ext4 at {p}".format(d=partition, p=path))
        return True

    print("Warning: {} usb is not mountable as ext4".format(partition))
    print("Attempting to mount with any filesystem...")

    if mnt_any(partition, path) == 0 and usb.is_mounted(partition):
        print(
            "{d} mounted at {p} with any filesystem".format(
                d=partition, p=path
            )
        )
        return True
    print(
        "Error: {} usb is not mountable with any supported format".format(
            partition
        )
    )
    print("Cannot continue without all USB storage devices")
    return False


def setup_fstab(device, mount):
    """Add device to fstab"""
    ext4_mounted = usb.is_mounted(device)
    if ext4_mounted:
        with open("/etc/fstab", "a") as file:
            fstab = "\nUUID={u} {m} ext4 defaults,noatime 0 0".format(
                u=usb.get_uuid(device), m=mount
            )
            file.write(fstab)
    else:
        print(
            "Warning: {} usb does not seem to be ext4 formatted".format(device)
        )
        print("{} will not be added to /etc/fstab".format(device))


def install_compose():
    print("Installing docker-compose, if necessary")
    call(["pip3", "install", "docker-compose==1.23.2"])


def create_swap():
    """Create swap on volatile usb device"""
    import psutil

    # TODO: make sure dd runs in foreground and is blocking
    print("Create swap on volatile usb device")
    volatile_path = Path("/media/volatile/volatile")
    volatile_path.mkdir(exist_ok=True)
    swap_path = volatile_path / "swap"

    def create_file():
        dd = run(
            [
                "dd",
                "if=/dev/zero",
                "of=/media/volatile/volatile/swap",
                "bs=1M",
                "count=1024",
            ],
            stdout=PIPE,
            stderr=STDOUT,
        )

        if dd.returncode != 0:
            # dd has non-zero exit code
            raise OSError(
                "Warning: dd cannot create swap file \n" + str(dd.stdout)
            )
        return True

    def mk_swap():
        mkswap = run(
            ["mkswap", "/media/volatile/volatile/swap"],
            stdout=PIPE,
            stderr=STDOUT,
        )

        if mkswap.returncode != 0:
            # mkswap has non-zero exit code
            raise OSError(
                "Warning: mkswap could not create swap file \n"
                + str(mkswap.stdout)
            )
        return True

    def swap_on():
        swapon = run(
            ["swapon", "/media/volatile/volatile/swap", "-p 100"],
            stdout=PIPE,
            stderr=STDOUT,
        )

        if swapon.returncode != 0:
            # swapon has non-zero exit code
            raise OSError(
                "Warning: swapon could not add to swap \n" + str(swapon.stdout)
            )
        return True

    def write_fstab():
        try:
            with open("/etc/fstab", "a") as file:
                file.write("\n/media/volatile/swap none swap sw,pri=100 0 0")
                print("Success! Wrote swap file to fstab")
                return True
        except Exception as error:
            print(error)
            print("Warning: could not add swap to /etc/fstab")
            raise

    if not volatile_path.is_dir():
        raise OSError("Warning: volatile directory inaccessible")

    if swap_path.is_file():
        print("Swap file exists")
        if psutil.swap_memory().total < 1000000000:
            print("Enabling swap")
            if swap_on() and enable_swap():
                return True
            return False
        return False

    if create_file() and mk_swap():
        if swap_on() and enable_swap():
            return write_fstab()


def check_to_fetch(file_path, url):
    """Check and fetch if necessary"""
    filename = file_path.split("/")[-1]
    path_list = file_path.split("/")[:-1]
    dir_path = "/".join(path_list)
    if Path(dir_path).is_dir():
        if Path(filename).is_file():
            print("Success {f} exists at {d}".format(f=filename, d=dir_path))
            return True
    else:
        try:
            Path(dir_path).mkdir(exist_ok=True)

            r = requests.get(url, stream=True)
            with open(filename, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            return True
        except Exception as error:
            print(error)
            return False


def usb_setup():
    """Perform setup on three usb devices"""
    largest = usb.largest_partition()
    medium = usb.medium_partition()
    smallest = usb.smallest_partition()
    devices = [largest, medium, smallest]
    mountpoints = ["/media/archive", "/media/volatile", "/media/important"]

    for device in devices:
        num = devices.index(device)
        if create_dir(mountpoints[num]):
            if fallback_mount(device, mountpoints[num]):
                # All good with mount and mount-point
                if check_for_destruction(device, mountpoints[num]):
                    device_name = mountpoints[num].split("/")[2]
                    mount_path = Path(
                        "{p}/{n}".format(p=mountpoints[num], n=device_name)
                    )
                    if mount_path.mkdir(exist_ok=True) and mount_path.is_dir():
                        # We confirmed device is mountable, readable, writable
                        setup_fstab(device, mountpoints[num])
            else:
                print(
                    "Mounting {d} with any filesystem unsuccessful".format(
                        d=device
                    )
                )
                exit(1)
        else:
            print(
                "Error: {p} directory not available".format(p=mountpoints[num])
            )
            exit(1)

    def setup_volatile():
        if usb.is_mounted(medium):
            if create_swap():
                enable_swap()
            else:
                print("Warning: Cannot create and enable swap!")
            setup_nginx()

    def setup_important():
        if usb.is_mounted(smallest):
            import noma.bitcoind

            print("Creating bitcoind files")
            noma.bitcoind.create()
            if noma.bitcoind.check():
                noma.bitcoind.set_prune("550")
                noma.bitcoind.set_rpcauth(
                    "/media/archive/archive/bitcoin/bitcoin.conf"
                )

            import noma.lnd

            print("Creating lnd files")
            noma.lnd.check_wallet()
            if noma.lnd.check():
                noma.lnd.setup_tor()

    def setup_archive():
        if usb.is_mounted(largest):
            import noma.bitcoind

            if noma.bitcoind.check():
                noma.bitcoind.fastsync()

    setup_volatile()
    setup_important()
    setup_archive()
    return True


def rc_add(service, runlevel=""):
    print("Enable {s} at boot".format(s=service))
    call(["rc-update", "add", service, runlevel])


def install_crontab():
    print("Installing crontab")
    exitcode = call(["/usr/bin/crontab", "/home/lncm/crontab"])
    return exitcode


def enable_compose():
    # TODO: Change init script to run "noma start" and "noma stop"
    print("Enable docker-compose at boot")
    check_to_fetch(
        "/etc/init.d/docker-compose",
        "https://raw.githubusercontent.com/lncm/pi-factory/b12c6f43d11be58dac03a2513cfd2abbb16f6526/etc/init.d/docker-compose",
    )
    exitcode = call(["rc-update", "add", "docker-compose"])
    return exitcode


def install_tor():
    add_tor = run(["apk", "add", "tor"])
    if add_tor.returncode == 0:
        start_tor = run(["/sbin/service", "tor", "start"])
        return start_tor.returncode


def install_box():
    import noma.node
    import noma.lnd

    is_installed = check_installed()
    if is_installed:
        print("Box installation detected!")

    move_cache()  # from FAT to ext4 on /var

    # apk
    apk_update()
    install_firmware()  # for raspberry-pi
    install_apk_deps()  # curl & jq; are these really necessary?
    install_compose()
    rc_add("dbus")
    rc_add("avahi-daemon")
    rc_add("docker")
    enable_compose()
    install_tor()
    rc_add("tor", "default")

    # html
    check_to_fetch(
        "/home/lncm/public_html/pos/index.html",
        "https://raw.githubusercontent.com/lncm/invoicer-ui/master/dist/index.html",
    )
    # check_to_fetch("home/lncm/public_html/wifi/index.html",
    #                "https://raw.githubusercontent.com/lncm/iotwifi-ui/master/dist/index.html")

    # containers
    print("Starting usb-setup")
    if usb_setup():
        print("Starting docker-compose")
        noma.node.start()
        install_crontab()
        if noma.lnd.check():
            print("Checking lnd wallet")
            noma.lnd.check_wallet()

    print("Removing post-install from default runlevel")
    call(["rc-update", "del", "lncm-post", "default"])


if __name__ == "__main__":
    print("This file is not meant to be run directly")
