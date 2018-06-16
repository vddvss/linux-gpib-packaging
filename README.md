This repo contains RPM spec files and patches for the 
[linux-gpib project](https://linux-gpib.sourceforge.io/) drivers and library for
GPIB (IEEE-488) adapters.

These are targeted at Fedora and RHEL/CentOS 7, but they can probably be made to
work with SUSE or other RPM distros, though I haven't bothered to put in all of
the logic to do that. The package also tries to adhere to the
[Fedora packaging guidelines](https://fedoraproject.org/wiki/Packaging:Guidelines).

# Installation

```bash
sudo dnf copr enable <name>/linux-gpib

# For a general installation that will require you to edit the gpib.conf file
sudo dnf install dkms-linux-gpib linux-gpib

# To include a gpib.conf file set up for Agilent/Keysight 82357A/B
# NOTE: you will also need to install the firmware package
sudo dnf install dkms-linux-gpib linux-gpib linux-gpib-defaults-agilent-82357a

# To include a gpib.conf file set up for NI-GPIB-USB-B/HS/HS+
# NOTE: for the NI-GPIB-USB-B, you will also need to install the firmware package
sudo dnf install dkms-linux-gpib linux-gpib linux-gpib-defaults-ni-gpib-usb
```

**IMPORTANT**: If you are using the HP/Agilent/Keysight 82357A, 82357B, 82341C,
82341D, or 82350A, or the NI GPIB-USB-B, you will also need to install the
appropriate firmware package available at
<https://github.com/<user>/linux-gpib-firmware-rpms>. No firmware is needed for
the NI-GPIB-USB-HS/HS+.

## Default Configurations
The repo contains the below packages with default configuration files for
popular USB GPIB adapters. For other configurations, you will need to edit the
`gpib.conf` file as 

| Adapter                   | Package Name                         |
| ------------------------- | ------------------------------------ |
| Agilent/Keysight 82357A/B | `linux-gpib-defaults-agilent-82357a` |
| NI-GPIB-USB-B/HS/HS+      | `linux-gpib-defaults-ni-gpib-usb`    |

## Extra Packages
The repo also contains bindings, documentation, and development packages:

| Type                | Package Name          |
| ------------------- | --------------------- |
| Development         | `linux-gpib-devel`    |
| Extra documentation | `linux-gpib-doc`      |
| Guile 1.8           | `guile18-linux-gpib`  |
| Perl                | `perl-LinuxGpib`      |
| Python 2            | `python2-linux-gpib`  |
| Python 3            | `python3-linux-gpib`  |
| Tcl                 | `tcl-linux-gpib`      |

# Device setup
These packages include new `udev` rules and an updated device initialization
process. When used with the `linux-gpib-defaults-*` packages, the device setup
should Just Work when using a single USB adapter, and the new rules should allow
greater flexibility when using multiple USB adapters.

If you have more than one adapter connected or if you want to change the minor
number for the gpib device node (e.g. for `/dev/gpib1`, the minor number is 1),
you will first need to edit the `gpib.conf` file. Details on this are available
[here](https://linux-gpib.sourceforge.io/doc_html/configuration-gpib-conf.html)
and [here](https://linux-gpib.sourceforge.io/doc_html/supported-hardware.html).

You will also need to add a custom `udev` rule in `/etc/udev/rules.d` to connect
the device to the minor number. The priority of the `udev` rule must be less
than 60.

For example, to setup an Agilent 52357B with the serial number MY12345678 that
you want to access at `/dev/gpib1`, you could add the following to 
`/etc/udev/rules.d/59-my-gpib-adapter.rules`. The minor device number is set by
the value of the `ID_GPIB_MINOR` variable.

```
ACTION=="add", SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", \
    ATTR{idVendor}=="0957", ATTR{idProduct}=="0718", \
    ENV{ID_SERIAL_SHORT}=="MY12345678", ENV{ID_GPIB_MINOR}="1"
```

Note that for the Agilent 82357B, the `ID_SERIAL_SHORT` may not be the same as
the number printed on your adapter--I think this may be an artifact of the
firmware upload. To find out the correct serial number to use, run 
`udevadm monitor -u -p`, plug in the adapter and look for the correct number.
For the NI-GPIB-USB-HS, you may need to prepend a 0 to the serial number printed
on your adapter (i.e. 1234567 becomes 01234567).

After doing this, run:

```bash
sudo udevadm control --reload
```

# Notes
These packages have only been tested on Fedora 28 with a Agilent/Keysight 82375B
USB adapter and a NI-GPIB-USB-HS adapter. Other versions of Fedora and other
adapters should work, but please open an issue or submit a pull request if you
run into problems.

## Patch notes
This repo contains several patches to upstream, including one to change the
`udev` rules to use a `uaccess` tag for the device nodes, instead of setting the
access mode and group. As a result, users will not need to be in the `gpib`
group in order to use the adapter, and the device will be accessible to logged
in users.

To restore the default behavior, create a file at
`/etc/udev/rules.d/61-linux-gpib-defaults.rules` with the following contents:

```
ACTION!="remove", KERNEL=="gpib[0-9]*", MODE="0660", GROUP="gpib", TAG-="uaccess"
```

After doing this, run:

```bash
sudo udevadm control --reload
```

If you have already plugged in an adapter (which loads the kernel module), you
will need to unplug it and run:

```bash
# for Agilent 82357A/B
sudo modprobe -r agilent_82357a gpib_common

# for NI-GPIB-* adapters
sudo modprobe -r ni_usb_gpib gpib_common
```

The priority of this `udev` rule must be greater than 60 but less than 70.

# Build Status

# Credits
There are quite a few installation guides and packaging specfiles for Linux-GPIB
floating around online, since installing and packaging Linux-GPIB can be
somewhat challenging. So credit goes to all those who have posted their
instructions.

In particular, the `dkms.conf` file is adapted from the
[Arch AUR linux-gpib-dkms repo](https://aur.archlinux.org/packages/linux-gpib-dkms/).
The [PLD Linux spec](https://github.com/pld-linux/linux-gpib/blob/master/linux-gpib.spec) 
was also quite helpful in putting this file together.

