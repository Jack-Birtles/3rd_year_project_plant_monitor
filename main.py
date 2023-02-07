# Jack Birtles
# Last updated 07/02/23
#
# A system to monitor and water house plants
# designed around the Raspberry Pi Pico W.

from machine import Pin, I2C, ADC
from time import sleep
# import RGB1602
from EPD_2in66 import EPD
# from neopixel import Neopixel
from settings import plant_details, network_details

usb_power = Pin(24, Pin.IN)        # high if on usb power
battery_type = "alkaline"          # either alakaline for 3 AA cells or lipo for lithium-ion

# strip = Neopixel(8, 1, 16, "GRB")

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
# lcd = RGB1602.RGB1602(16,2)
epd = EPD(152, 296, 12, 8, 9, 13)

const_air_val = 51500
const_water_val = 26600
read_delay = 5        # read moisture every n seconds

# def setupLCD():
#     lcd.setRGB(255,255,255)
#     lcd.setCursor(0,0)
#     lcd.printout("Moisture Level:")
#     lcd.setCursor(0,1)
#     lcd.printout("Initialising")
    
# def updateLCD(value):
#     lcd.setCursor(0,1)
#     lcd.printout("                ")
#     lcd.setCursor(0,1)
#     lcd.printout(value)

#   Calculates a rough value for the remaining battery percentage.
#   Might be better just waiting till the battery voltage reaches 
#   just above the minimal supply voltage for the pico and then 
#   warning the user. This could then use the same method for both AAs and Lipo packs.
# def batteryLevel():
#     if lower(battery_type) == alkaline:
#         if voltage >= 1.55:
#             return 100
#         elif 1.4 < voltage < 1.55
#             return ((60.6 * voltage) + 6.1) # needs rounding to int
#         elif 1.1 <= voltage <= 1.4:
#             return (9400 - (23000 * voltage) + (19000 * voltage * voltage * voltage)) # round to int  
#         elif 0 < v < 1.1:
#             return (8.3 * voltage) # round to int
#         else:
#             return 0
            
#     elif lower(battery_type) == lipo
#         return 0
    
#     else:
#         # battery type set incorrectly
#         return 0

def refreshEP():
    # epd.Clear(0xff) # 0xff is white, 0x00 black
    epd.fill(0xff)
    epd.display(epd.buffer)
    print("Refreshed")
    # epd.sleep()

def updateEP(value):
    refreshEP()
    epd.text("Moisture Level: ", 13, 10, 0x00)
    epd.text(value, 13, 40, 0x00)
    epd.display(epd.buffer)
    # epd.sleep()
    print("Updated")
    
def relativeChange(old_val, new_val):
    change = abs(((new_val - old_val) / old_val) * 100)
    return round(change)
    
# refreshEP()
# sleep(2)
last_moisture_val = 0
if usb_power:
    # initialise web page for remote sensor reading
    # enable neopixel stick to give clear indication if situation
    # is good or bad - maybe take all sensor values and have a continuum for the resulting colour?         
    while True:
        onboard_led.toggle()
        sensor_value = soil.read_u16()
        moisture = (const_air_val - sensor_value) * 100 / (const_air_val - const_water_val)
        print("moisture: " + "%.2f" % moisture +"% (adc: "+str(sensor_value)+")")

        if (last_moisture_val == 0) or (relativeChange(last_moisture_val, moisture) > 5):
            moisture_percent = "%.2f" % moisture +"%"
            updateEP(moisture_percent)
            last_moisture_val = moisture
        # updateLCD(moisture_percent)
        
        sleep(read_delay)
else:
    # no web page and lower refresh rate for lower power draw
    # maybe include a power saving mode that will sleep the system and just wakeup every while to check sensors
    while True:
        onboard_led.toggle()
        sleep(1)
    
    
    
    

# if __name__=='__main__':
#     epd = EPD_2in66(152, 296, 12, 8, 9, 13)
#     epd.Clear(0xff)
    
#     epd.fill(0xff)
#     epd.text("Waveshare", 13, 10, 0x00)
#     epd.text("Pico_ePaper-2.66", 13, 40, 0x00)
#     epd.text("Raspberry Pico", 13, 70, 0x00)
#     epd.display(epd.buffer)
#     utime.sleep_ms(2000)
    
#     epd.vline(10, 90, 60, 0x00)
#     epd.vline(140, 90, 60, 0x00)
#     epd.hline(10, 90, 130, 0x00)
#     epd.hline(10, 150, 130, 0x00)
#     epd.line(10, 90, 140, 150, 0x00)
#     epd.line(140, 90, 10, 150, 0x00)
#     epd.display(epd.buffer)
#     utime.sleep_ms(2000)
    
#     epd.rect(10, 180, 60, 80, 0x00)
#     epd.fill_rect(80, 180, 60, 80, 0x00)
#     utime.sleep_ms(2000)
    
#     epd.init(1)
#     for i in range(0, 10):
#         epd.fill_rect(52, 270, 40, 20, 0xff)
#         epd.text(str(i), 72, 270, 0x00)
#         epd.display(epd.buffer)

#     epd.init(0)
#     epd.Clear(0xff)
#     utime.sleep_ms(2000)
#     print("sleep")
#     epd.sleep()