#!/usr/bin/python3
import argparse
import json
from pathlib import Path

usbdevs = Path('/sys/bus/usb/devices/')

# Device properties that will be read by default, so they are
# available for logging even if not used for device selection. All
# elements in this set refer to per-device sysfs files of the same
# name.
properties = {'product', 'manufacturer', 'idProduct', 'idVendor'}

# Wakeup will be disabled for any device matching any of the entries
# in this list. You can use all standard file sysfs file names as
# keys. Values are compared ignoring case.
disable_wakeup = [
    {'product': 'USB keyboard'}
]


def print_device_info(dev, dev_props):
    print(dev)
    for key, value in dev_props.items():
        print(f'  {key}: {value}')
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Disable wakeup from suspend for select USB devices.')
    parser.add_argument('--config', '-c', type=Path, default=None,
                        help='load configuration from this JSON file')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='disable informational output, log only for '
                        'which devices wakeup is getting disabled')
    args = parser.parse_args()

    if args.config is not None:
        with open(args.config) as fh:
            config = json.load(fh)
        disable_wakeup = config.get('disable_wakeup', disable_wakeup)
        properties |= set(*(d.keys() for d in disable_wakeup))

    for dev in usbdevs.iterdir():
        try:
            dev_props = dict(
                (prop, (dev / prop).read_text().strip())
                for prop in properties)
        except FileNotFoundError:
            # Subdevices don't have all the properties, but we don't need
            # to look at those.
            continue

        if not args.quiet:
            print_device_info(dev, dev_props)

        for d in disable_wakeup:
            if all(dev_props[k].lower() == d[k].lower() for k in d.keys()):
                print(f'Device {dev} matches {d}, disabling wakeup.')
                (dev / 'power/wakeup').write_text('disabled')
                break
