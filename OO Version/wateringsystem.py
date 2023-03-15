from machine import Pin, PWM, ADC, I2C
from time import sleep

from am2320 import AM2320

const_air_val = 51500
const_water_val = 26600
weights = [0.025, 0.1, 0.175, 0.2, 0.5]


class WateringSystem:
    """_summary_
    """

    def __init__(self) -> None:
        self.onboard_led = Pin("LED", Pin.OUT)
        self.button = Pin(6, Pin.IN, Pin.PULL_DOWN)
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
        for i,j in enumerate(values):
            average = average + (j * weights[i])

        if is_moisture:
            average = round((const_air_val - average) * 100 /
                            (const_air_val - const_water_val), 1)
        return average

    def watering_cycle(self):
        self.onboard_led.high()
        self.pump.duty_u16(1000)
        sleep(30)
        self.pump.duty_u16(0)

    def enable_waterpump(self):
        self.onboard_led.high()
        self.pump.duty_u16(1000)

    def disable_waterpump(self):
        self.onboard_led.high()
        self.pump.duty_u16(0)    
