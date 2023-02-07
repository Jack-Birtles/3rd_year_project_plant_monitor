from machine import Pin
from time import sleep

usb_power = Pin(24, Pin.IN)
onboard_led = Pin("LED", Pin.OUT)

while True:
    if usb_power:
        onboard_led.toggle()
        sleep(2)
    else:
        sleep(2)