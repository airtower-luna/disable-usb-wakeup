#!/usr/bin/python3
from pathlib import Path

usbdevs = Path('/sys/bus/usb/devices/')

# Device properties that can be used to select a device. All elements
# in this list refer to per-device sysfs files of the same name.
properties = ['product', 'manufacturer', 'idProduct', 'idVendor']

# Wakeup will be disabled for any device matching any of the entries
# in this list. You can use all items in "properties" as keys
# here. Values are compared ignoring case.
disable_wakeup = [
    {'product': 'USB keyboard'}
]

def print_device_info(dev, dev_props):
    print(dev)
    for key, value in dev_props.items():
        print(f'  {key}: {value}')
    print()

if __name__ == '__main__':
    for dev in usbdevs.iterdir():
        try:
            dev_props = dict(
                (prop, (dev / prop).read_text().strip()) for prop in properties)
        except FileNotFoundError:
            # Subdevices don't have all the properties, but we don't need
            # to look at those.
            continue

        print_device_info(dev, dev_props)

        for d in disable_wakeup:
            if all(dev_props[k].lower() == d[k].lower() for k in d.keys()):
                print(f'Matching device for {d} found, disabling wakeup.')
                (dev / 'power/wakeup').write_text('disabled')
                break
