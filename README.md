# Disable wakeup from suspend for select USB devices

I noticed that my cat sometimes pulls my computer out of suspend by
walking across the keyboard during the night. :paw_prints: So I
decided to disable waking up the system via the keyboard, and this is
the result. Now my computer should sleep well, too, instead of wasting
power all night. :smile_cat:

## How it works

The script checks the sysfs entries for your USB devices, which can be
found in `/sys/bus/usb/devices/`. The files within the device
directory contain (among other thing) information that identifies the
device, like its type or manufacturer. The script compares these
against a configured list, and on a match it writes `disabled` to the
`power/wakeup` file for the device. This should work on any Linux
system. :penguin:

## Installation

Just copy the script to a suitable location and copy the systemd unit
to the system units directory, then enable it:

```sh
sudo cp disable-usb-wakeup.py /etc/
sudo cp disable-usb-wakeup.service /etc/systemd/system/
systemctl enable disable-usb-wakeup.service
```

You can use another location for the script, just adjust the
`ExecStart` line in the service unit accordingly. You should **not**
use a script file owned by a regular (non-root) user, because then it
could be used for privilege escalation: That user could edit the file
to have the systemd unit do just about anything.

The unit is configured to start before `sleep.target`. The reason why
I don't use `multi-user.target` is that re-plugging a device resets
its wakeup setting, and I want the unit to work regardless of whether
the device has been unplugged at any point after boot.

For other init systems you'll have to use their means to run the
script at the right time.

## Configuration

The default configuration contained in the script disables wakeup for
all USB keyboards. If that doesn't suit your needs, you can create a
JSON configuration file, for example like this if don't want your
computer to wake up on any USB mouse, and also not for the device with
vendor ID `1234` and product ID `abcd`:

```json
{
    "disable_wakeup": [
        {"product": "usb mouse"},
        {"idVendor": "1234", "idProduct": "abcd"}
    ]
}
```

The properties of each item in the `disable_wakeup` list are compared
against the properties of each USB device, and wakeup set to disabled
for each match.

Once you have your configuration file change the `ExecStart` line in
the systemd unit to use it, for example:

```
ExecStart=/etc/disable-usb-wakeup.py -q -c /path/to/config.json
```
