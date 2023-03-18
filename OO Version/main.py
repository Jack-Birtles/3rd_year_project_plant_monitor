# Jack Birtles
# Last updated 15/03/23
#
# Contains the main logic for a plant monitoring system

from time import sleep, sleep_ms
from machine import Pin, ADC, Timer, lightsleep
import uasyncio

from wateringsystem import WateringSystem

from EPD_2in66 import EPD
from ws2812b import Neopixel_Controller
from webserver import webServer

from settings import plant_details, network_details

watering_system = WateringSystem()
epaper = EPD(152, 296, 12, 8, 9, 13)
neopixel_stick = Neopixel_Controller(16, 8)
power_source = Pin(24, Pin.IN)        # high if on usb power
usb_power_flag = power_source.value()
battery_voltage = ADC(27)
button = Pin(6, Pin.IN, Pin.PULL_DOWN)
timer = Timer(-1)

sleep_duration = int(plant_details["update_time"])
watering_threshold = int(plant_details["minimum_moisture_percentage"])
disable_watering_flag = False
low_battery_threshold = 3.75
low_battery_flag = False


def refreshEP():
    epaper.fill(0xff)
    epaper.display(epaper.buffer)
    print("Refreshed")


def updateEP(moisture, temperature, humidity):
    refreshEP()
    epaper.text("Moisture Level: ", 13, 10, 0x00)
    epaper.text(str(moisture), 13, 40, 0x00)
    epaper.text("Temperature: ", 13, 70, 0x00)
    epaper.text(str(temperature), 13, 100, 0x00)
    epaper.text("Humidity Level: ", 13, 130, 0x00)
    epaper.text(str(humidity), 13, 160, 0x00)
    epaper.display(epaper.buffer)
    print("Updated")


def enable_watering():
    global disable_watering_flag
    disable_watering_flag = False
    print("watering now enabled")


def watering_interrupt(button, watering_system):
    button.irq(trigger=0)
    sleep_ms(300)
    if button.value() == 1:
        watering_system.enable_waterpump()
        while button.value() == 1:
            sleep(1)
        watering_system.disable_waterpump()
    button.irq(trigger=Pin.IRQ_RISING, handler=lambda t: watering_interrupt(button, watering_system))


def get_battery_voltage() -> float:
    raw_value = battery_voltage.read_u16()
    voltage = (raw_value * (3.3 / 65536)) * 2
    return voltage


async def main():
    if usb_power_flag:
        web_server.connect()


    while True:
        watering_system.read_sensors()
        refreshEP()
        updateEP(watering_system.moisture_average,
                 watering_system.temp_average,
                 watering_system.humidity_average)

        if (watering_system.moisture_average < watering_threshold) and (not disable_watering_flag):
            neopixel_stick.fill((255, 0, 0), 0.05)
            for i in range(1):
                watering_system.enable_waterpump()
                sleep(10)
                watering_system.disable_waterpump()
                sleep(1)
            if low_battery_flag:
                neopixel_stick.fill((255, 0, 0), 0.05)
            else:
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
        sleep(sleep_duration)
        # for i in range(1000):
        #     lightsleep(2)
        # sleep(1)
        print("awake")




web_server = webServer(network_details)
button.irq(trigger=Pin.IRQ_RISING, handler=lambda t: watering_interrupt(button, watering_system))
uasyncio.run(main())
uasyncio.new_event_loop()
