from machine import Pin, I2C, ADC
from time import sleep
import RGB1602
from neopixel import Neopixel

usb_power = Pin(24, Pin.IN)        # high if on usb power

strip = Neopixel(8, 1, 16, "GRB")

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
lcd = RGB1602.RGB1602(16,2)

const_air_val = 51500
const_water_val = 26600
read_delay = 5        # read moisture every n seconds

def setupLCD():
    lcd.setRGB(255,255,255)
    lcd.setCursor(0,0)
    lcd.printout("Moisture Level:")
    lcd.setCursor(0,1)
    lcd.printout("Initialising")
    
def updateLCD(value):
    lcd.setCursor(0,1)
    lcd.printout("                ")
    lcd.setCursor(0,1)
    lcd.printout(value)


setupLCD()
sleep(2)
while True:
    onboard_led.toggle()
    sensor_value = soil.read_u16()
    moisture = (const_air_val - sensor_value) * 100 / (const_air_val - const_water_val)
    print("moisture: " + "%.2f" % moisture +"% (adc: "+str(sensor_value)+")")
    moisture_percent = "%.2f" % moisture +"%" 
    updateLCD(moisture_percent)
    
    sleep(read_delay)