from machine import Pin, ADC, I2C, lightsleep
from network import WLAN, STA_IF
import uasyncio
from time import sleep
from EPD_2in66 import EPD
from am2320 import AM2320
# from neopixel import Neopixel
from settings import plant_details, network_details

usb_power = Pin(24, Pin.IN)        # high if on usb power
battery_voltage = ADC(27)

# strip = Neopixel(8, 1, 16, "GRB")

red = (255, 0, 0)
orange = (255, 50, 0)
yellow = (255, 100, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (100, 0, 90)
violet = (200, 0, 100)
colors_rgb = [red, orange, yellow, green, blue, indigo, violet,]

onboard_led = Pin("LED", Pin.OUT)
soil = ADC(Pin(26))
temp_humidity = AM2320(i2c=I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))

epd = EPD(152, 296, 12, 8, 9, 13)

const_air_val = 51500
const_water_val = 26600
read_delay = 5        # read moisture every n seconds

moisture_values = []
temperature_values = []
humidity_values = []
sensor_averages = {"moisture"    : "Initialising",
                   "temperature" : "Initialising",
                   "humidity"    : "Initialising",
                   "light"       : "Initialising",}



def refreshEP():
    epd.fill(0xff)
    epd.display(epd.buffer)
    print("Refreshed")
    # epd.sleep()

def updateEP(moisture, temperature, humidity):
    refreshEP()
    epd.text("Moisture Level: ", 13, 10, 0x00)
    epd.text(moisture, 13, 40, 0x00)
    epd.text("Temperature: ", 13, 70, 0x00)
    epd.text(temperature, 13, 100, 0x00)
    epd.text("Humidity Level: ", 13, 130, 0x00)
    epd.text(humidity, 13, 160, 0x00)
    epd.display(epd.buffer)
    # epd.sleep()
    print("Updated")

def updateSensorReading():
    soil_value = soil.read_u16()
    moisture = (const_air_val - soil_value) * 100 / (const_air_val - const_water_val)
    



if usb_power:
    # using uasyncio to allow responding to web requests while
    # periodically scanning the sensors
    try:
        uasyncio.run(main())
    finally:
        uasyncio.new_event_loop()
else:
    # when running on battery power:
    # no web page and lower refresh rate for lower power draw
    # also sleeping the pico with lightsleep
    while True:
        updateSensorReadings()
        lightsleep(10000)