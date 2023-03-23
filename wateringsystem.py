# Jack Birtles
# Last updated 23/03/23
#
# Contains driver code for controlling a peristaltic pump,
# capacitive moisture sensor and AM2320 sensor.

from time import sleep

from machine import ADC, I2C, PWM, Pin

from am2320 import AM2320

const_air_val = 51500
const_water_val = 26600
weights = [[1], [0.2, 0.8], [0.1, 0.2, 0.7], [0.05, 0.125, 0.225, 0.6],
           [0.025, 0.1, 0.175, 0.2, 0.5]]


class WateringSystem:
    """
    Controls a peristaltic pump, capacitive moisture sensor and an
    AM2320 temperature and humidity sensor

    Attributes:
        pump (PWM): PWM object to control the pump
        soil (ADC): ADC source of the moisture sensor
        temp_humidity (AM2320): Driver for the AM2320 sensor
        moisture_values (List): last 5 moisture readings
        moisture_average (int): weighted average calculated from the above list
        temp_values (List): last 5 temperature readings
        temp_average (int): weighted average calculated from the above list
        humidity_values (List): last 5 humidity readings
        humidity_average (int): weighted average calculated from the above list
    """

    def __init__(self) -> None:
        self.pump = PWM(Pin(5))
        self.pump.freq(50)
        self.soil = ADC(Pin(26))
        self.temp_humidity = AM2320(
            i2c=I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))

        self.moisture_values = []
        self.moisture_average = 0
        self.temp_values = []
        self.temp_average = 0
        self.humidity_values = []
        self.humidity_average = 0

    def read_sensors(self) -> None:
        current_reading = self.soil.read_u16()
        self.moisture_values.append(current_reading)
        if len(self.moisture_values) > 5:
            self.moisture_values.pop(0)
        self.moisture_average = self.update_average(self.moisture_values, True)

        current_reading = self.temp_humidity.temperature()
        self.temp_values.append(current_reading)
        if len(self.temp_values) > 5:
            self.temp_values.pop(0)
        self.temp_average = self.update_average(
            self.temp_values, False)

        current_reading = self.temp_humidity.humidity()
        self.humidity_values.append(current_reading)
        if len(self.humidity_values) > 5:
            self.humidity_values.pop(0)
        self.humidity_average = self.update_average(
            self.humidity_values, False)

    def update_average(self, values, is_moisture):
        average = 0
        for i, j in enumerate(values):
            average = average + (j * weights[len(values) - 1][i])

        if is_moisture:
            average = round((const_air_val - average) * 100 /
                            (const_air_val - const_water_val), 1)
        return average

    def watering_cycle(self):
        self.pump.duty_u16(1000)
        # sleep(60)
        sleep(10)
        self.pump.duty_u16(0)

    def enable_waterpump(self):
        self.pump.duty_u16(1000)

    def disable_waterpump(self):
        self.pump.duty_u16(0)
