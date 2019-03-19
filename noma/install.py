from pathlib import Path
from shutil import copy
from subprocess import call, Popen, PIPE
from time import sleep
from noma import usb


def create_mount_points():
    print("Create mount points")
    Path('/media/important').mkdir()
    Path('/media/volatile').mkdir()
    Path('/media/archive').mkdir()


def check_installed():
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
    print("Let apk cache live on persistent volume")
    cache_dir = Path("/media/mmcblk0p1/cache")
    if cache_dir.is_dir():
        copy(cache_dir, "/var/cache/apk/")
        call(["setup-apkcache", "/var/cache/apk"])


def enable_swap():
    print("Enable swap at boot")
    call(["rc-update", "add", "swap", "boot"])


def install_firmware():
    print("Install raspberry-pi firmware")
    call(["apk", "add", "raspberrypi"])


def apk_update():
    print("Update package repository")
    call(["apk", "update"])


def install_apk_deps():
    print("Install curl and jq")
    call(["apk", "add", "curl", "jq"])





def mnt_ext4(device, path):
    call(["mount", "-t ext4 /dev/" + device, path])


def mnt_any(device, path):
    call(["mount", "/dev/" + device, path])


def mount_usb_devices():
    mount_usb_dev(usb.largest_partition(), "/media/archive")
    mount_usb_dev(usb.medium_partition(), "/media/volatile")
    mount_usb_dev(usb.smallest_partition(), "/media/important")


def setup_nginx():
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
        copy(origin, destination)


def check_and_destroy(device):
    print("Check devices for destruction flag")
    destroy = Path("/media/" + device + "DESTROY_ALL_DATA_ON_THIS_DEVICE.txt").is_file()
    if destroy:
        print("Going to destroy all data on /dev/%s in 3 seconds...") % device
        sleep(3)
        call(["mkfs.ext4", "-F", "/dev/" + usb.largest_partition()])
        mnt_ext4("/dev/" + usb.largest_partition(), "/media/" + device)
    else:
        print("Device is not flagged for being wiped")


def check_all():
    check_and_destroy("archive")
    check_and_destroy("important")
    check_and_destroy("volatile")


def mount_usb_dev(partition, path):
    print("Mount ext4 storage devices")
    print(partition)

    mnt_ext4(partition, path)
    ext4_mountable = usb.is_mounted(partition)

    if not ext4_mountable:
        print("Warning: %s usb is not mountable as ext4") % partition
        mnt_any(partition, path)
        mountable = usb.is_mounted(partition)
        if not mountable:
            print("Error: %s usb is not mountable as any supported format") % partition
            print("Cannot continue without all USB storage devices")
            exit(1)


def setup_fstab(device):
    # TODO: check mount status with psutil instead
    ext4_mounted = Path("/media/" + device + "/lost+found").is_dir()
    if ext4_mounted:
        with open("/etc/fstab", 'a') as file:
            fstab = "\nUUID=%s /media/%s ext4 defaults,noatime 0 0" % usb.get_uuid(device), device
            file.write(fstab)
    else:
        print("Warning: %s usb does not seem to be ext4 formatted") % device
        print("%s will not be added to /etc/fstab") % device


def setup_fstab_all():
    setup_fstab("archive")
    setup_fstab("volatile")
    setup_fstab("important")


def create_swap():
    print("Create swap on volatile usb device")
    volatile_path = Path("/media/volatile/volatile")
    volatile_path.mkdir()

    if not volatile_path.is_dir():
        print("Warning: volatile directory inaccessible")

    dd = Popen(["dd", "if=/dev/zero", "of=/media/volatile/volatile/swap", "bs=1M", "count=1024"],
               stdout=PIPE,
               stderr=PIPE)

    if dd.returncode:
        # dd has non-zero exit code
        print("Warning: dd cannot create swap file")

    mkswap = Popen(["mkswap", "/media/volatile/volatile/swap"],
                   stdout=PIPE,
                   stderr=PIPE)

    if mkswap.returncode:
        # mkswap has non-zero exit code
        print("Warning: mkswap could not create swap file")

    swapon = Popen(["swapon", "/media/volatile/volatile/swap", "-p 100"],
                   stdout=PIPE,
                   stderr=PIPE)

    if swapon.returncode:
        # swapon has non-zero exit code
        print("Warning: swapon could not add to swap")

    try:
        with open("/etc/fstab", 'a') as file:
            file.write("\n/media/volatile/swap none swap sw,pri=100 0 0")
    except Exception as error:
        print(error)
        print("Warning: could not add swap to /etc/fstab")


if __name__ == "__main__":
    print("This file is not meant to be run directly")
