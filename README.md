
# ON POWESHELL
# https://learn.microsoft.com/en-us/windows/wsl/connect-usb
# winget install --interactive --exact dorssel.usbipd-win
# usbipd list
#   Connected:
#   BUSID  VID:PID    DEVICE                                                        STATE
#   2-2    239a:8029  USB Serial Device (COM9)                                      Not shared
#
# AS ADMIN
#   ENABLE
# usbipd bind   --busid 2-2
#   DISABLE
# usbipd detach --busid 2-2
#
# AS USER
# usbipd attach --wsl --busid 2-2
#
# ON LINUX
# lsusb
#   Bus 001 Device 002: ID 239a:8029 Adafruit T1000-E-BOOT
#
# ls /dev/serial/by-id/ -l
#   lrwxrwxrwx 1 root root 13 Nov  5 22:34 usb-Seeed_Studio_T1000-E-BOOT_ -> ../../ttyACM0

# https://devblogs.microsoft.com/commandline/connecting-usb-devices-to-wsl/
# https://github.com/dorssel/usbipd-win/wiki/WSL-support#usbip-client-tools
# https://github.com/dorssel/usbipd-win/issues/646

sudo apt install build-essential flex bison libssl-dev libelf-dev libncurses-dev autoconf libudev-dev libtool
sudo apt install linux-tools-virtual hwdata
sudo apt install linux-tools-common

sudo update-alternatives --install /usr/local/bin/usbip  usbip  `ls /usr/lib/linux-tools/*/usbip  | tail -n1` 20
sudo update-alternatives --install /usr/local/bin/usbipd usbipd `ls /usr/lib/linux-tools/*/usbipd | tail -n1` 20

python3 -m venv .venv
source .venv/bin/activate
#pip3 install --upgrade pytap2
#pip3 install --upgrade meshtastic
#pip3 install --upgrade duckdb
pip3 install --upgrade -r requirements.txt

meshtastic

mkdir nodes/
NODE=
meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --export-config > nodes/${NODE}.yaml
meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --info          > nodes/${NODE}.info
meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --nodes         > nodes/${NODE}.nodes

meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --listen
