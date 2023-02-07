from machine import Pin, ADC
from time import sleep
# import RGB1602
from EPD_2in66 import EPD
# from neopixel import Neopixel

usb_power = Pin(24, Pin.IN)        # high if on usb power
battery_type = "alkaline"          # either alakaline for 3 AA cells or lipo for lithium-ion

red = (255, 0, 0)
orange = (255, 50, 0)
yellow = (255, 100, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (100, 0, 90)
violet = (200, 0, 100)
colors_rgb = [red, orange, yellow, green, blue, indigo, violet]

onboard_led = Pin("LED", Pin.OUT)
soil = ADC(Pin(26))
epd = EPD(152, 296, 12, 8, 9, 13)

const_air_val = 51500
const_water_val = 26600
read_delay = 5        # read moisture every n seconds


def refreshEP():
    epd.fill(0xff)
    epd.display(epd.buffer)

def updateEP(value):
    refreshEP()
    epd.text("Moisture Level: ", 13, 10, 0x00)
    epd.text(value, 13, 40, 0x00)
    epd.display(epd.buffer)
    
def relativeChange(old_val, new_val):
    change = abs(((new_val - old_val) / old_val) * 100)
    return round(change)


last_moisture_val = 0
if usb_power:     
    while True:
        onboard_led.toggle()
        sensor_value = soil.read_u16()
        moisture = (const_air_val - sensor_value) * 100 / (const_air_val - const_water_val)
        print("moisture: " + "%.2f" % moisture +"% (adc: "+str(sensor_value)+")")

        if (last_moisture_val == 0) or (relativeChange(last_moisture_val, moisture) > 5):
            moisture_percent = "%.2f" % moisture +"%"
            updateEP(moisture_percent)
            last_moisture_val = moisture
        
        sleep(read_delay)
else:
    while True:
        onboard_led.toggle()
        sleep(1)