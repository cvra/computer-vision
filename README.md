# Installation

Create a virtualenv and source it, use python 3.5. Then

    pushd planReader
    pip install -r requirements.txt
    pip install .
    popd

You should be able to run the script

    python grab_and_detect.py

## Serial port configuration

First enable it on the pi

Edit `/boot/config.txt` with

    dtparam=uart0=on
    dtparam=uart1=on
    enable_uart=1

## Connect the to the Raspberry Pi over wifi

The raspi runs a wifi hotspot `PrimeMover`, you can connect to it.
The hotspot was setup reading these instructions https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

## Configure serial port

Follow instructions https://www.raspberrypi.org/documentation/configuration/uart.md

## Configure SSH over USB

Follow instructions https://www.thepolyglotdeveloper.com/2016/06/connect-raspberry-pi-zero-usb-cable-ssh/
Static IP set following https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-gadget
Remember to set ip in the DHCP file, not /etc/network/interfaces, otherwise the DHCP server won't start and the hotspot won't work simultaneously.

So the pi can be accessed via USB, at static IP 192.168.7.2
