from ws2812b import Neopixel_Controller
from time import sleep
from machine import Pin, PWM, ADC, I2C, Timer, lightsleep

strip = Neopixel_Controller(16, 8)


# OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)


while (True):
    for color in COLORS:
        strip.fill(color, 0.05)
        read_onboard_voltage()
        sleep(5)
