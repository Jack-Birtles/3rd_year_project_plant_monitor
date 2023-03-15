from time import sleep
from machine import Pin, PWM, ADC, I2C, Timer, lightsleep

from wateringsystem import WateringSystem

from EPD_2in66 import EPD
from ws2812b import Neopixel_Controller

watering_system = WateringSystem()
epaper = EPD(152, 296, 12, 8, 9, 13)
neopixel_stick = Neopixel_Controller(16, 8)
usb_power = Pin(24, Pin.IN)        # high if on usb power
battery_voltage = ADC(27)

timer = Timer(-1)
watering_threshold = 40
disable_watering_flag = False
low_battery_threshold = 3.75
low_battery_flag = False


def refreshEP():
    # epd.Clear(0xff) # 0xff is white, 0x00 black
    epaper.fill(0xff)
    epaper.display(epaper.buffer)
    print("Refreshed")
    # epd.sleep()


def updateEP(moisture, temperature, humidity):
    refreshEP()
    epaper.text("Moisture Level: ", 13, 10, 0x00)
    epaper.text(str(moisture), 13, 40, 0x00)
    epaper.text("Temperature: ", 13, 70, 0x00)
    epaper.text(str(temperature), 13, 100, 0x00)
    epaper.text("Humidity Level: ", 13, 130, 0x00)
    epaper.text(str(humidity), 13, 160, 0x00)
    epaper.display(epaper.buffer)
    # epd.sleep()
    print("Updated")


def enable_watering():
    global disable_watering_flag
    disable_watering_flag = False
    print("watering now enabled")


def low_power_warning():
    pass


def get_battery_voltage() -> float:
    raw_value = battery_voltage.read_u16()
    voltage = (raw_value * (3.3 / 65536)) * 2
    return voltage


while True:
    watering_system.read_sensors()
    refreshEP()
    updateEP(watering_system.moisture_average,
             watering_system.temp_average, watering_system.humidity_average)

    if (watering_system.moisture_average < watering_threshold) and (not disable_watering_flag):
        neopixel_stick.fill((255, 0, 0), 0.05)
        for i in range(1):
            watering_system.enable_waterpump()
            sleep(10)
            watering_system.disable_waterpump()
            sleep(1)
        neopixel_stick.fill((0, 0, 0), 0.05)
        disable_watering_flag = True
        print("watering finished", disable_watering_flag)
        timer.init(period=900000, mode=Timer.ONE_SHOT,
                   callback=lambda t: enable_watering())

    if usb_power.value() == 0:
        if not low_battery_flag:
            voltage = get_battery_voltage()
            if voltage < low_battery_threshold:
                low_battery_flag = True
                neopixel_stick.fill((255, 0, 0), 0.05)

    print("sleeping")
    sleep(60)
    # for i in range(1000):
    #     lightsleep(2)
    # sleep(1)
    print("awake")
