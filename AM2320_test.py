from machine import Pin, I2C
from time import sleep
# from EPD_2in66 import EPD
from am2320 import AM2320

onboard_led = Pin("LED", Pin.OUT)
# epd = EPD(152, 296, 12, 8, 9, 13)
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
temp_humidity = AM2320(i2c=i2c)

readDelay = 5

# def refreshEP():
#     # epd.Clear(0xff) # 0xff is white, 0x00 black
#     epd.fill(0xff)
#     epd.display(epd.buffer)
#     print("Refreshed")
#     # epd.sleep()

# def updateEP(temp_value, hum_value):
#     refreshEP()
#     epd.text("Temperature: ", 13, 10, 0x00)
#     epd.text(temp_value, 13, 40, 0x00)
#     epd.text("Humidity: ", 13, 10, 0x00)
#     epd.text(hum_value, 13, 40, 0x00)
#     epd.display(epd.buffer)
#     # epd.sleep()
#     print("Updated")


while True:
    # temp_humidity.measure()
    print(temp_humidity.temperature())
    print(temp_humidity.humidity())
    
    sleep(readDelay)