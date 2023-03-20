from time import sleep
from machine import Pin, PWM, ADC, I2C

from am2320 import AM2320
from EPD_2in66 import EPD


# def setServoCycle(position):
#     pwm.duty_u16(position)
#     sleep(0.5)


# def start_watering():
#     onboard_led.high()
#     pwm.duty_u16(1000)
#     sleep(30)
#     pwm.duty_u16(0)


class WateringSystem:
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """

    def __init__(self) -> None:
        self.onboard_led = Pin("LED", Pin.OUT)
        self.button = Pin(6, Pin.IN, Pin.PULL_DOWN)
        self.pump = PWM(Pin(5))
        self.pump.freq(50)
        self.soil = ADC(Pin(26))
        self.temp_humidity = AM2320(
            i2c=I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))

        self.const_air_val = 51500
        self.const_water_val = 26600

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
        average = sum(values) / len(values)
        if is_moisture:
            average = round((self.const_air_val - average) * 100 /
                            (self.const_air_val - self.const_water_val), 1)
        return average


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


system = WateringSystem()
while True:
    # while button.value():
    #     onboard_led.high()
    #     # for pos in range(1000, 9000, 50):
    #     #     # setServoCycle(pos)
    #     #     pwm.duty_u16(pos)
    #     #     sleep(0.1)
    #     pwm.duty_u16(1000)
    #     # sleep(0.01)

    # pwm.duty_u16(0)
    # onboard_led.low()
    system.read_sensors()
