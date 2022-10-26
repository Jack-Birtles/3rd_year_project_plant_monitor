from machine import Pin, I2C
from time import sleep
#import RGB1602

#import blinka
import board
import busio
from TSL2561 import TSL2561

pin = Pin("LED", Pin.OUT)
# lcd=RGB1602.RGB1602(16,2)

i2c = busio.I2C(board.GP10, board.GP9)
tsl2561 = TSL2561(i2c)

# def setupLCD():
#     lcd.setRGB(255,255,255)
#     lcd.setCursor(0,0)
#     lcd.printout("Hello World")
#     lcd.setCursor(0,1)
#     lcd.printout("Fucking finally!")


# setupLCD()
while True:
    pin.toggle()
    
    print('Lux: {}'.format(i2c.lux))
    print('Broadband: {}'.format(i2c.broadband))
    print('Infrared: {}'.format(i2c.infrared))
    print('Luminosity: {}'.format(i2c.luminosity))
    
    sleep(1)