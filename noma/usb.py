"""
USB and SD device related functionality
"""
from os import path
from os import popen
from sys import exit
import glob
import re
import psutil
from subprocess import call

# TODO: handle mountable devices without partitions!

USB_DEV_PATTERN = ["sd.*"]
USB_PART_PATTERN = ["sd.[1-9]*"]
SD_DEV_PATTERN = ["mmcblk*"]
SD_PART_PATTERN = ["mmcblk.p[1-9]*"]


def is_mounted(device):
    """Check if a device is already mounted

    :param device: device or device + partition number
    :type device: string, e.g. "sda1"
    :return: True/False if device is mounted or not
    :rtype: bool
    """

    partitions = psutil.disk_partitions()
    device_path = "/dev/" + device
    for i in partitions:
        if i.device == device_path:
            return True
    return False


def fs_size(fs_path):
    """Return filesystem size in bytes

    :param fs_path: path to mounted filesystem
    :return: filesystem size in bytes
    """
    import shutil

    total, used, free = shutil.disk_usage(fs_path)
    return total


def dev_size(device):
    """Return device size in bytes

    :param device: device
    :type device: string, e.g. "sda"
    :return: device size in bytes
    :rtype: int
    """
    device_path = "/sys/block/"
    num_sectors = open(device_path + device + "/size").read().rstrip("\n")
    sector_size = (
        open(device_path + device + "/queue/hw_sector_size")
        .read()
        .rstrip("\n")
    )
    return int(num_sectors) * int(sector_size)


def usb_part_size(partition):
    """Return USB partition size in bytes

    :param partition: device
    :type partition: string, e.g. "sda"
    :return: partition size in bytes
    :rtype: int
    """
    try:
        device_path = "/sys/block/"
        device = partition[:-1]
        num_sectors = (
            open(device_path + device + "/" + partition + "/size")
            .read()
            .rstrip("\n")
        )
        sector_size = (
            open(device_path + device + "/queue/hw_sector_size")
            .read()
            .rstrip("\n")
        )
    except TypeError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return int(num_sectors) * int(sector_size)


def sd_part_size(partition):
    """Return SD partition size in bytes

    :param partition: device
    :type partition: string, e.g. "sda"
    :return: partition size in bytes
    :rtype: int
    """
    try:
        device_path = "/sys/block/"
        device = partition[:-1]
        num_sectors = (
            open(device_path + device + "/" + partition + "/size")
            .read()
            .rstrip("\n")
        )
        sector_size = (
            open(device_path + device + "/queue/hw_sector_size")
            .read()
            .rstrip("\n")
        )
    except TypeError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return int(num_sectors) * int(sector_size)


def usb_devs():
    """list usb devices"""
    devices = []
    for device in glob.glob("/sys/block/*"):
        for pattern in USB_DEV_PATTERN:
            if re.compile(pattern).match(path.basename(device)):
                devices.append(path.basename(device))
    return devices


def sd_devs():
    """list sd devices"""
    devices = []
    for device in glob.glob("/sys/block/*"):
        for pattern in SD_DEV_PATTERN:
            if re.compile(pattern).match(path.basename(device)):
                devices.append(path.basename(device))
    return devices


def usb_partitions():
    """list usb partitions"""
    partitions = []
    for device in usb_devs():
        for partition in glob.glob("/sys/block/" + str(device) + "/*"):
            for pattern in USB_PART_PATTERN:
                if re.compile(pattern).match(path.basename(partition)):
                    partitions.append(path.basename(partition))
    return partitions


def sd_partitions():
    """list sd partitions"""
    partitions = []
    for device in sd_devs():
        for partition in glob.glob("/sys/block/" + str(device) + "/*"):
            for pattern in SD_PART_PATTERN:
                if re.compile(pattern).match(path.basename(partition)):
                    partitions.append(path.basename(partition))
    return partitions


def usb_partition_table():
    """list usb partition sizes"""
    table = {}
    for partition in usb_partitions():
        table[partition] = int(usb_part_size(partition))
    return table


def sd_partition_table():
    """list sd partition sizes"""
    table = {}
    for partition in sd_partitions():
        table[partition] = sd_part_size(partition)
    return table


def sd_device_table():
    """list sd devices"""
    table = {}
    for device in sd_devs():
        table[device] = dev_size(device)
    return table


def usb_device_table():
    """list usb devices"""
    table = {}
    for device in usb_devs():
        table[device] = dev_size(device)
    return table


def sort_partitions():
    """sort partitions from smallest to largest"""
    usb_partitions = usb_partition_table()
    sorted_partitions = sorted(usb_partitions.items(), key=lambda x: x[1])
    return sorted_partitions


def largest_partition():
    """get largest device and partition name"""
    try:
        usb_partitions = sort_partitions()
        last = len(usb_partitions) - 1
        largest = usb_partitions[last]
    except IndexError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return str(largest[0])


def smallest_partition():
    """get third largest device and partition name"""
    try:
        usb_partitions = sort_partitions()
        smallest = usb_partitions[0]
    except IndexError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return str(smallest[0])


def medium_partition():
    """get second largest device and partition name"""
    try:
        usb_partitions = sort_partitions()
        usb_partitions.pop(0)  # remove smallest
        usb_partitions.pop(len(usb_partitions) - 1)  # remove largest
    except IndexError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return str(usb_partitions[0][0])


def largest_part_size():
    """get partition size in bytes of largest partition"""
    return usb_part_size(largest_partition())


def uuid_table():
    """list UUIDs of all block devices
    e.g. {'sdc1': 'd641d2b9-4fcd-4c83-9415-7ca4e7553a5d'}

    :return: dictionary of device names and UUIDs"""
    device_table = popen("blkid").read().splitlines()
    devices = {}
    for device in device_table:
        dev = device.split(":")[0].split("/")[2]
        uuid = device.split('UUID="')[1].split('"')[0]
        devices[dev] = uuid
    return devices


def get_uuid(device):
    """get uuid of device"""
    uuids = uuid_table()
    return str(uuids[device])


def usb_setup():
    """start usb-setup with 3 devices"""
    print("Warning: using deprecated usb_setup routine!")
    largest = largest_partition()
    medium = medium_partition()
    smallest = smallest_partition()

    print("Starting USB installation")
    print("Using {} as archive storage".format(largest))
    print("Using {} as volatile storage".format(medium))
    print("Using {} as important storage".format(smallest))

    lncm_usb = "/usr/local/sbin/lncm-usb"

    cli_invocation = [
        lncm_usb,
        largest,
        medium,
        smallest,
        get_uuid(largest),
        get_uuid(medium),
        get_uuid(smallest),
        str(largest_part_size()),
    ]

    call(cli_invocation)


if __name__ == "__main__":
    print("This file is not meant to be run directly")
