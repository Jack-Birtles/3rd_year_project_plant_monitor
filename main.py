# Jack Birtles
# Last updated 23/03/23
#
# Contains the main logic for a plant monitoring system

from re import search
from time import sleep, sleep_ms

import uasyncio
import ujson
from machine import ADC, Pin, Timer, lightsleep

from EPD_2in66 import EPD
from networkhelper import networkHelper
from wateringsystem import WateringSystem
from ws2812b import Neopixel_Controller


class main:
    """
    A class to control general functionality of the plant monitor

    Attributes:
        sleep_duration (int): time to sleep between updates
        watering_threshold (int): moisture level to begin watering
        connection (networkHelper): network controller
        watering_system (WateringSystem): sensor and pump controller
        epaper (EPD): epaper controller
        neopixel_stick (Neopixel_Controller): neopixel controller
        power_source (Pin): battery indicator
        usb_power_flag (bool): current power source (True with USB power)
        battery_voltage (ADC): pin location of the halved battery voltage
        button (Pin): pin location of the watering button
        timer (Timer): software timer instance
        manual_watering_flag (bool): indicator of current manual pump usage
        disable_watering_flag (bool): indicator of recent watering
        low_battery_threshold (float): voltage to trigger low battery warning
        low_battery_flag (bool): indicator that low battery is acknowledged

    """

    def __init__(self):
        settings = self.get_settings()
        network_details = {
            "name": settings["name"],
            "password": settings["password"]}
        self.sleep_duration = int(settings["update_time"])
        self.watering_threshold = int(settings["minimum_moisture_percentage"])

        self.connection = networkHelper(network_details)
        self.watering_system = WateringSystem()
        self.epaper = EPD(152, 296, 12, 8, 9, 13)
        self.neopixel_stick = Neopixel_Controller(16, 8)
        self.power_source = Pin(24, Pin.IN)        # high if on usb power
        self.usb_power_flag = self.power_source.value()
        self.battery_voltage = ADC(27)
        self.button = Pin(6, Pin.IN, Pin.PULL_DOWN)
        self.timer = Timer(-1)
        self.timer_b = Timer(-1)

        self.manual_watering_flag = False
        self.disable_watering_flag = False
        self.low_battery_threshold = 3.75
        self.low_battery_flag = False

        self.button.irq(trigger=Pin.IRQ_RISING,
                        handler=lambda t: self.watering_interrupt(self.button))

    def get_settings(self) -> dict:
        """Retrieves user settings from config.json

        Returns:
            settings converted to dictionary format
        """

        file = open("config.json", "r")
        settings = ujson.loads(file.read())
        file.close()
        return settings

    def change_settings(self, new_sleep_duration, new_watering_threshold):
        """Saves new settings values to the config file

        Args:
            new_sleep_duration (int): updated value for time
                                      to sleep between updates
            new_watering_threshold (int): updated value for the level
                                          to begin automatic watering
        """

        file = open("config.json", "r")
        file_data = ujson.loads(file.read())
        file_data["update_time"] = new_sleep_duration
        file_data["minimum_moisture_percentage"] = new_watering_threshold
        file = open("config.json", "w")
        file.write(ujson.dumps(file_data))
        file.close()

        self.sleep_duration = int(new_sleep_duration)
        self.watering_threshold = int(new_watering_threshold)

    def refreshEP(self):
        """Clear the epaper and empty the buffer
        """

        self.epaper.fill(0xff)
        self.epaper.display(self.epaper.buffer)

    def updateEP(self, moisture, temperature, humidity, connection=""):
        """Update the sensor values and connection status shown on the display

        Args:
            moisture (float): moisture level
            temperature (float): temperature in Celsius
            humidity (float): relative humidity
            connection (str, optional): connection status, only included if
                                        on mains power. Defaults to "".
        """

        self.refreshEP()
        self.epaper.text("Moisture Level (%): ", 2, 10, 0x00)
        self.epaper.text(str(moisture), 2, 40, 0x00)
        self.epaper.text("Temperature (C): ", 2, 70, 0x00)
        self.epaper.text(str(temperature), 2, 100, 0x00)
        self.epaper.text("Humidity Level (%): ", 2, 130, 0x00)
        self.epaper.text(str(humidity), 2, 160, 0x00)

        if connection != "":
            self.epaper.text("Connection Status: ", 2, 190, 0x00)
            self.epaper.text(connection, 2, 220, 0x00)
        self.epaper.display(self.epaper.buffer)

    def enable_watering(self):
        """Changes the state of the watering flag
        """

        self.disable_watering_flag = False
        print("Watering enabled")

    def disable_watering(self):
        """Changes the state of the watering flag and sets a timer to enable it in 15 minutes
        """

        self.disable_watering_flag = True
        self.timer.init(period=900000, mode=Timer.ONE_SHOT,
                        callback=lambda t: self.enable_watering())
        print("Watering disabled")

    def watering_interrupt(self, button):
        """Handler for manual watering. Pump stays on while button is held

        Args:
            button (Pin): GPIO pin connected to a button
        """

        # Disable interrupt to stop multiple triggers
        button.irq(trigger=0)
        # Sleep long enough to debounce switch
        sleep_ms(300)

        if button.value() == 1:
            self.watering_system.enable_waterpump()
            while button.value() == 1:
                sleep(1)
            self.watering_system.disable_waterpump()
        button.irq(trigger=Pin.IRQ_RISING,
                   handler=lambda t: self.watering_interrupt(button))

    def get_battery_voltage(self) -> float:
        """Reads the divided battery input and converts it into volts

        Returns:
            float: Rough battery voltage
        """

        raw_value = self.battery_voltage.read_u16()
        voltage = (raw_value * (3.3 / 65536)) * 2
        return voltage

    async def serveClient(self, reader, writer):
        """Asynchronously respond to http requests for the webserver

        Args:
            reader : Reads http requests
            writer : Responds to http requests
        """

        page = self.connection.get_webpage("index.html")

        print("client connected")
        request_line = await reader.readline()
        print("request: ", request_line)

        while await reader.readline() != b"\r\n":
            pass

        request = str(request_line)
        response = page
        watering_on = request.find("/state=1")
        watering_off = request.find("/state=0")
        settings_changed = request.find("threshold=")

        # Replace placeholders with up to date values
        response = response.replace(
            "moistureValue", str(self.watering_system.moisture_average))
        response = response.replace(
            "temperatureValue", str(self.watering_system.temp_average))
        response = response.replace(
            "humidityValue", str(self.watering_system.humidity_average))
        response = response.replace(
            "thresholdValue", str(self.watering_threshold))
        response = response.replace(
            "updateValue", str(self.sleep_duration))

        if watering_on == 6:
            self.manual_watering_flag = True
            self.watering_system.enable_waterpump()
            self.disable_watering()
        elif watering_off:
            self.watering_system.disable_waterpump()
            self.manual_watering_flag = False
            self.enable_watering()
        if self.manual_watering_flag:
            response.replace("not_checked", "checked")

        if settings_changed == 7:
            new_threshold = search("_(.+?)_", request).group(1)
            new_update = search("~(.+?)~", request).group(1)
            self.change_settings(new_update, new_threshold)

        writer.write("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        writer.write(response)

        await writer.drain()
        await writer.wait_closed()
        print("client disconnecting")

    async def main(self):
        """Main loop containing logic to control when to read sensors and responding to their outputs
        """

        # Webserver is only used when on mains power
        connection_status = ""
        if self.usb_power_flag == 0:
            self.connection.connect()
            connection_status = self.connection.get_ip()
            uasyncio.create_task(uasyncio.start_server(
                self.serveClient, "0.0.0.0", 80))

        while True:
            self.watering_system.read_sensors()
            self.refreshEP()
            self.updateEP(round(self.watering_system.moisture_average, 1),
                          round(self.watering_system.temp_average, 1),
                          round(self.watering_system.humidity_average, 1),
                          connection_status)

            if (self.watering_system.moisture_average < self.watering_threshold) and (not self.disable_watering_flag):
                self.neopixel_stick.fill((255, 0, 0), 0.05)
                self.watering_system.enable_waterpump()
                self.timer_b.init(period=60000, mode=Timer.ONE_SHOT,
                                  callback=lambda t: self.watering_system.disable_waterpump())

                if self.low_battery_flag:
                    self.neopixel_stick.fill((255, 0, 0), 0.05)
                else:
                    self.neopixel_stick.fill((0, 0, 0), 0.05)
                self.disable_watering()

            if not self.usb_power_flag:
                if not self.low_battery_flag:
                    voltage = self.get_battery_voltage()
                    if voltage < self.low_battery_threshold:
                        self.low_battery_flag = True
                        self.neopixel_stick.fill((255, 0, 0), 0.05)

            print("sleeping")
            if self.usb_power_flag == 0:
                await uasyncio.sleep(self.sleep_duration)
            else:
                # Lightsleep lowers power consumption but has RAM and
                # state retention
                lightsleep(self.sleep_duration)


main_instance = main()
uasyncio.run(main_instance.main())
