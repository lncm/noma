from pathlib import Path
import shutil
from subprocess import call, Popen, PIPE
from time import sleep
from noma import usb
import requests


def create_dir(path):
    Path(path).mkdir()
    if Path(path).is_dir():
        return True
    return False


def check_installed():
    """Check if LNCM-Box is installed"""
    installed = "/media/mmcblk0p1/installed"
    if Path(installed).is_file():
        with open(installed, 'r') as file:
            lines = file.readlines()
            for line in lines:
                print(line)
        return True
    else:
        return False


def move_cache():
    """Let apk cache live on persistent volume"""
    print("Let apk cache live on persistent volume")
    cache_dir = Path("/media/mmcblk0p1/cache")
    if cache_dir.is_dir():
        shutil.copy(cache_dir, "/var/cache/apk/")
        call(["setup-apkcache", "/var/cache/apk"])


def enable_swap():
    """Enable swap at boot"""
    print("Enable swap at boot")
    call(["rc-update", "add", "swap", "boot"])
    call(["rc-update", "add", "swap", "default"])


def install_firmware():
    """Install raspberry-pi firmware"""
    print("Install raspberry-pi firmware")
    call(["apk", "add", "raspberrypi"])


def apk_update():
    """Update apk mirror repositories"""
    print("Update package repository")
    call(["apk", "update"])


def install_apk_deps():
    """Install dependencies curl and jq"""
    print("Install curl and jq")
    call(["apk", "add", "curl", "jq"])


def mnt_ext4(device, path):
    """Mount device at path using ext4"""
    call(["mount", "-t ext4 /dev/" + device, path])


def mnt_any(device, path):
    """Mount device at path using any filesystem"""
    call(["mount", "/dev/" + device, path])


def setup_nginx():
    """Setup nginx paths and config files"""
    nginx_volatile = Path("/media/volatile/volatile/nginx/").is_dir()
    if nginx_volatile:
        print("Nginx volatile directory found")
    else:
        print("Creating nginx volatile directory")
        Path("/media/volatile/volatile/nginx").mkdir()
    nginx_important = Path("/media/important/important/nginx").is_dir()
    if nginx_important:
        print("Nginx important directory found")
    else:
        print("Copying nginx config to important media")
        destination = Path("/media/important/important/nginx")
        origin = Path("/etc/nginx")
        shutil.copy(origin, destination)


def check_for_destruction(device):
    """Check devices for destruction flag. If so, format with ext4"""
    print("Check devices for destruction flag")
    destroy = Path("/media/" + device + "DESTROY_ALL_DATA_ON_THIS_DEVICE.txt").is_file()
    if destroy:
        print("Going to destroy all data on /dev/%s in 3 seconds...") % device
        sleep(3)
        call(["umount", "/dev/" + device])
        sleep(1)
        if not usb.is_mounted(device):
            print("Going to format {d} with ext4 now".format(d=device))
            call(["mkfs.ext4", "-F", "/dev/" + device])
            mnt_ext4("/dev/" + device, "/media/" + device)
            sleep(1)
            if usb.is_mounted(device):
                print("{d} formatted with ext4 successfully and mounted.".format(d=device))
                return True
        else:
            call(["umount", "-f", "/dev/" + device])
            sleep(1)
            if not usb.is_mounted(device):
                print("Going to format {d} with ext4 now".format(d=device))
                call(["mkfs.ext4", "-F", "/dev/" + device])
                mnt_ext4("/dev/" + device, "/media/" + device)
                sleep(1)
                if usb.is_mounted(device):
                    print("{d} formatted with ext4 successfully and mounted.".format(d=device))
                    return True
            else:
                print("Error mounting {}".format(device))
                return False
    else:
        print("Device is not flagged for being wiped")
        return True


def fallback_mount(partition, path):
    """Attempt to mount partition at path using ext4 first and falling back to any

    :return bool: success
    """
    print("Mount ext4 storage device:")
    print(partition)

    mnt_ext4(partition, path)
    sleep(1)
    ext4_mountable = usb.is_mounted(partition)

    if not ext4_mountable:
        print("Warning: %s usb is not mountable as ext4") % partition
        mnt_any(partition, path)
        sleep(1)
        mountable = usb.is_mounted(partition)
        if not mountable:
            print("Error: %s usb is not mountable as any supported format") % partition
            print("Cannot continue without all USB storage devices")
            return False
    else:
        return True


def setup_fstab(device):
    """Add device to fstab"""
    ext4_mounted = usb.is_mounted(device)
    if ext4_mounted:
        with open("/etc/fstab", 'a') as file:
            fstab = str("\nUUID=%s /media/%s ext4 defaults,noatime 0 0" % usb.get_uuid(device), device)
            file.write(fstab)
    else:
        print("Warning: %s usb does not seem to be ext4 formatted") % device
        print("%s will not be added to /etc/fstab") % device


def create_swap():
    """Create swap on volatile usb device"""
    print("Create swap on volatile usb device")
    volatile_path = Path("/media/volatile/volatile")
    volatile_path.mkdir()

    if not volatile_path.is_dir():
        print("Warning: volatile directory inaccessible")
        return False

    dd = Popen(["dd", "if=/dev/zero", "of=/media/volatile/volatile/swap", "bs=1M", "count=1024"],
               stdout=PIPE,
               stderr=PIPE)

    if dd.returncode:
        # dd has non-zero exit code
        print("Warning: dd cannot create swap file")
        return False

    mkswap = Popen(["mkswap", "/media/volatile/volatile/swap"],
                   stdout=PIPE,
                   stderr=PIPE)

    if mkswap.returncode:
        # mkswap has non-zero exit code
        print("Warning: mkswap could not create swap file")
        return False

    swapon = Popen(["swapon", "/media/volatile/volatile/swap", "-p 100"],
                   stdout=PIPE,
                   stderr=PIPE)

    if swapon.returncode:
        # swapon has non-zero exit code
        print("Warning: swapon could not add to swap")
        return False

    try:
        with open("/etc/fstab", 'a') as file:
            file.write("\n/media/volatile/swap none swap sw,pri=100 0 0")
            print("Success! Wrote swap file to fstab")
            return True
    except Exception as error:
        print(error)
        print("Warning: could not add swap to /etc/fstab")
        return False


def check_to_fetch(file_path, url):
    """Check and fetch if necessary"""
    filename = file_path.split('/')[-1]
    path_list = file_path.split('/')[:-1]
    dir_path = '/'.join(path_list)
    if Path(dir_path).is_dir():
        if Path(filename).is_file():
            print("Success {f} exists at {d}".format(f=filename, d=dir_path))
            return True
    else:
        try:
            Path(dir_path).mkdir()

            r = requests.get(url, stream=True)
            with open(filename, 'wb') as f:
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
        for mountpoint in mountpoints:
            if create_dir(mountpoint):
                if fallback_mount(device, mountpoint):
                    sleep(1)
                    if usb.is_mounted(device):
                        print("Mounting {d} at {p} successful".format(d=device, p=mountpoint))
                        # All good with mount and mount-point
                        if check_for_destruction(device):
                            setup_fstab(device)
                    else:
                        print('Error: {d} is not mounted'.format(d=device))
                        exit(1)
                else:
                    print('Mounting {d} with any filesystem unsuccessful'.format(d=device))
                    exit(1)
            else:
                print("Error: {p} directory not available".format(p=mountpoint))

    # volatile
    if usb.is_mounted(medium):
        if create_swap():
            enable_swap()
        else:
            print("Warning: Cannot create and enable swap!")
        setup_nginx()

    # important
    if usb.is_mounted(smallest):
        import noma.bitcoind
        noma.bitcoind.create()
        if noma.bitcoind.check():
            noma.bitcoind.set_prune("550")
            noma.bitcoind.set_rpcauth("/media/archive/archive/bitcoin/bitcoin.conf")

        import noma.lnd
        noma.lnd.create()
        if noma.lnd.check():
            noma.lnd.setup_tor()

    # archive
    if usb.is_mounted(largest):
        import noma.bitcoind
        if noma.bitcoind.check():
            noma.bitcoind.fastsync()


def install_crontab():
    print("Installing crontab")
    call(["/usr/bin/crontab", "/home/lncm/crontab"])


def enable_compose():
    print("Enable docker-compose at boot")
    call(["rc-update", "add", "docker-compose", "default"])


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

    # html
    check_to_fetch("/home/lncm/public_html/pos/index.html",
                   "https://raw.githubusercontent.com/lncm/invoicer-ui/master/dist/index.html")
    check_to_fetch("home/lncm/public_html/wifi/index.html",
                   "https://raw.githubusercontent.com/lncm/iotwifi-ui/master/dist/index.html")

    # containers
    usb_setup()
    enable_compose()
    noma.node.start()
    install_crontab()
    if noma.lnd.check():
        noma.lnd.check_wallet()


if __name__ == "__main__":
    print("This file is not meant to be run directly")
