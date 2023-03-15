# Jack Birtles
# Last updated 07/02/23
#
# A system to monitor and water house plants
# designed around the Raspberry Pi Pico W.

from machine import Pin, ADC, I2C
from network import WLAN, STA_IF
import uasyncio
from time import sleep
# import RGB1602
from EPD_2in66 import EPD
from am2320 import AM2320
# from neopixel import Neopixel - this might already be included on latest micropython RP2 port
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
colors_rgb = [red, orange, yellow, green, blue, indigo, violet]

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
light_values = []
sensor_averages = {"moisture"    : "Initialising",
                   "temperature" : "Initialising",
                   "humidity"    : "Initialising",
                   "light"       : "Initialising", }


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

def connect(network):
    ssid = network["name"]
    pswd = network["password"]

    status_values = ["LINK_DOWN", "LINK_JOIN", "LINK_NOIP", "LINK_UP",
                     "LINK_FAIL", "LINK_NONET", "LINK_BADAUTH"]

    wlan = WLAN(STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pswd)

    wait_time = 10
    while wait_time > 0:
        if 0 > wlan.status() >= 3:
            break
        wait_time -= 1
        print("Connecting...")
        sleep(1)

    if wlan.status() != 3:
        print(status_values[wlan.status()])
        raise RuntimeError("network connection failed")
    else:
        print("connected")
        print(status_values[wlan.status()])
        status = wlan.ifconfig()
        print("ip = " + status[0])

def getWebpage(file):
    try:
        with open(file, "r") as f:
            page = f.read()
    except Exception as e:
        print(e, "\nfile does not exist")
        raise e

    return page

async def serveClient(reader, writer):
    page = getWebpage("production/index.html")


    print("client connected")
    request_line = await reader.readline()
    print("request: ", request_line)

    while await reader.readline() != b"\r\n":
        pass

    # request = str(request_line)


    response = page
    response = response.replace("moistureValue", sensor_averages["moisture"])
    response = response.replace("temperatureValue", sensor_averages["temperature"])
    response = response.replace("humidityValue", sensor_averages["humidity"])
    response = response.replace("lightValue", sensor_averages["light"])
    writer.write("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    print("client disconnecting")

async def main():
    connect(network_details)
    print("Setting up webserver")
    uasyncio.create_task(uasyncio.start_server(serveClient, "0.0.0.0", 80))

    last_moisture_val = 0
    while True:
        soil_value = soil.read_u16()
        moisture = round((const_air_val - soil_value) * 100 / (const_air_val - const_water_val), 1)
        print("moisture: " + "%.1f" % moisture +"% (adc: "+str(soil_value)+")")
        updateSensorReadings()

        temperature_value = temp_humidity.temperature()
        sensor_averages["temperature"] = str(temperature_value) + " Celsius"    #u"\u2103" for degrees C
        print("temperature: " + sensor_averages["temperature"])

        humidity_value = temp_humidity.humidity()
        sensor_averages["humidity"] = str(humidity_value) + "%"
        print("humidity: " + sensor_averages["humidity"])

        if (last_moisture_val == 0) or (relativeChange(last_moisture_val, moisture) > 5):
            sensor_averages["moisture"] = "%.2f" % moisture +"%"
            updateEP(sensor_averages["moisture"], sensor_averages["temperature"], sensor_averages["humidity"])
            last_moisture_val = moisture
        await uasyncio.sleep(read_delay)

def refreshEP():
    # epd.Clear(0xff) # 0xff is white, 0x00 black
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
    
def relativeChange(old_val, new_val):
    change = abs(((new_val - old_val) / old_val) * 100)
    return round(change)

def updateSensorReadings():
    soil_value = soil.read_u16()
    moisture = round((const_air_val - soil_value) * 100 / (const_air_val - const_water_val), 1)
    new_moisture_values, sensor_averages["moisture"] = calcRollingAverage(moisture, moisture_values)
    moisture_values = new_moisture_values
    print("moisture: " + "%.1f" % moisture +"%")

    # temperature_value = temp_humidity.temperature()
    # sensor_averages["temperature"] = str(temperature_value) + " Celsius"    #u"\u2103" for degrees C
    # print("temperature: " + sensor_averages["temperature"])

    # humidity_value = temp_humidity.humidity()
    # sensor_averages["humidity"] = str(humidity_value) + "%"
    # print("humidity: " + sensor_averages["humidity"])

def calcRollingAverage(reading, value_list):
    value_list.append(reading)
    list_length = len(value_list)
    if list_length == 11:
        value_list.remove(0)
    total = sum(value_list)
    return value_list, str((total / list_length))
    

last_moisture_val = 0
if usb_power:
    # using aysnc to allow responding to web requests while
    # periodically scanning the sensors
    try:
        uasyncio.run(main())
    finally:
        uasyncio.new_event_loop()
    print("BAD")
    # enable neopixel stick to give clear indication if situation
    # is good or bad - maybe take all sensor values and have a continuum for the resulting colour?         
    # while True:
    #     onboard_led.toggle()
    #     sensor_value = soil.read_u16()
    #     moisture = (const_air_val - sensor_value) * 100 / (const_air_val - const_water_val)
    #     print("moisture: " + "%.2f" % moisture +"% (adc: "+str(sensor_value)+")")

    #     if (last_moisture_val == 0) or (relativeChange(last_moisture_val, moisture) > 5):
    #         moisture_percent = "%.2f" % moisture +"%"
    #         updateEP(moisture_percent)
    #         last_moisture_val = moisture
    #     # updateLCD(moisture_percent)
        
    #     sleep(read_delay)
else:
    # no web page and lower refresh rate for lower power draw
    # maybe include a power saving mode that will sl
    #   3AAs will range ~3v to 4.5v
    #   turn on low voltage indicator at ~3.3v?
    while True:
        onboard_led.toggle()
        sleep(1)
        # machine.deepsleep([time_ms]
        # machine.lightsleep([time_ms]
        # - power saving, need to test which sleep is required