#!/usr/bin/env python3

from os import path
from os import popen
from sys import exit
import glob
import re
from subprocess import call

# TODO: handle mountable devices without partitions!

usb_dev_pattern = ['sd.*']
usb_part_pattern = ['sd.[1-9]*']
sd_dev_pattern = ['mmcblk*']
sd_part_pattern = ['mmcblk.p[1-9]*']


def is_mounted(device):
    import psutil
    partitions = psutil.disk_partitions()
    device_path = "/dev/" + device
    for i in partitions:
        if i.device == device_path:
            return True
    return False


def dev_size(device):
    # return device size in bytes
    device_path = '/sys/block/'
    num_sectors = open(device_path + device + '/size').read().rstrip('\n')
    sector_size = open(device_path + device + '/queue/hw_sector_size').read().rstrip('\n')
    return int(num_sectors)*int(sector_size)


def usb_part_size(partition):
    try:
        # return partition size in bytes
        device_path = '/sys/block/'
        device = partition[:-1]
        num_sectors = open(device_path + device + '/' + partition + '/size').read().rstrip('\n')
        sector_size = open(device_path + device + '/queue/hw_sector_size').read().rstrip('\n')
    except TypeError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return int(num_sectors)*int(sector_size)


def sd_part_size(partition):
    try:
        # return partition size in bytes
        device_path = '/sys/block/'
        device = partition[:-2]
        num_sectors = open(device_path + device + '/' + partition + '/size').read().rstrip('\n')
        sector_size = open(device_path + device + '/queue/hw_sector_size').read().rstrip('\n')
    except TypeError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return int(num_sectors)*int(sector_size)


def usb_devs():
    devices = []
    for device in glob.glob('/sys/block/*'):
        for pattern in usb_dev_pattern:
            if re.compile(pattern).match(path.basename(device)):
                devices.append(path.basename(device))
    return devices


def sd_devs():
    devices = []
    for device in glob.glob('/sys/block/*'):
        for pattern in sd_dev_pattern:
            if re.compile(pattern).match(path.basename(device)):
                devices.append(path.basename(device))
    return devices


def usb_partitions():
    partitions = []
    for device in usb_devs():
        for partition in glob.glob('/sys/block/' + str(device) + '/*'):
            for pattern in usb_part_pattern:
                if re.compile(pattern).match(path.basename(partition)):
                    partitions.append(path.basename(partition))
    return partitions


def sd_partitions():
    partitions = []
    for device in sd_devs():
        for partition in glob.glob('/sys/block/' + str(device) + '/*'):
            for pattern in sd_part_pattern:
                if re.compile(pattern).match(path.basename(partition)):
                    partitions.append(path.basename(partition))
    return partitions


def usb_partition_table():
    table = {}
    for partition in usb_partitions():
        table[partition] = int(usb_part_size(partition))
    return table


def sd_partition_table():
    table = {}
    for partition in sd_partitions():
        table[partition] = sd_part_size(partition)
    return table


def sd_device_table():
    table = {}
    for device in sd_devs():
        table[device] = dev_size(device)
    return table


def usb_device_table():
    table = {}
    for device in usb_devs():
        table[device] = dev_size(device)
    return table


def sort_partitions():
    # sort partitions from smallest to largest
    usb_partitions = usb_partition_table()
    sorted_partitions = sorted(usb_partitions.items(), key=lambda x: x[1])
    return sorted_partitions


def largest_usb_partition():
    try:
        usb_partitions = sort_partitions()
        last = len(usb_partitions) - 1
        largest = usb_partitions[last]
    except IndexError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return str(largest[0])


def smallest_usb_partition():
    try:
        usb_partitions = sort_partitions()
        smallest = usb_partitions[0]
    except IndexError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return str(smallest[0])


def medium_usb_partition():
    try:
        usb_partitions = sort_partitions()
        usb_partitions.pop(0)   # remove smallest
        usb_partitions.pop(len(usb_partitions) - 1)   # remove largest
    except IndexError:
        print("Not enough USB devices available")
        exit(1)
    else:
        return str(usb_partitions[0][0])


def largest_usb_part_size():
    return usb_part_size(largest_usb_partition())


def uuid_table():
    device_table = popen('blkid').read().splitlines()
    devices = {}
    for device in device_table:
        dev = device.split(":")[0].split("/")[2]
        uuid = device.split('"')[1]
        devices[dev] = uuid
    return devices


def get_uuid(device):
    uuids = uuid_table()
    return str(uuids[device])


def usb_setup():
    largest = largest_usb_partition()
    medium = medium_usb_partition()
    smallest = smallest_usb_partition()

    print('Starting USB installation')
    print('Using %s as archive storage') % largest
    print('Using %s as volatile storage') % medium
    print('Using %s as important storage') % smallest

    lncm_usb = "/usr/local/sbin/lncm-usb"

    cli_invocation = ' '.join([lncm_usb,
                               largest,
                               medium,
                               smallest,
                               get_uuid(largest),
                               get_uuid(medium),
                               get_uuid(smallest),
                               str(largest_usb_part_size())])

    call([cli_invocation])


if __name__ == "__main__":
    print("This file is not meant to be run directly")
