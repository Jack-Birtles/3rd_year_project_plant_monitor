# Jack Birtles
# Last updated 07/02/23
#
# All wifi setup is done here before the Pico finishes initialising

import rp2
# from machine import Pin
# from time import sleep
# import network


# usb_power = Pin(24, Pin.IN)        # high if on usb power

# Set wireless driver to use correct settings if required.
rp2.country("GB")