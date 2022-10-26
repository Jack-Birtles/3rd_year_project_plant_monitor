from machine import Pin, I2C, ADC
from time import sleep
import RGB1602

onboard_led = Pin("LED", Pin.OUT)
soil = ADC(Pin(26))
lcd = RGB1602.RGB1602(16,2)

#min_moisture = 0
#max_moisture = 65535

min_moisture = 25000
max_moisture = 50000
readDelay = 5

def setupLCD():
    lcd.setRGB(255,255,255)
    lcd.setCursor(0,0)
    lcd.printout("Moisture Level:")
    lcd.setCursor(0,1)
    lcd.printout("Initialising")
    
def updateLCD(value):
    lcd.setCursor(0,1)
    lcd.printout("                ")
    lcd.setCursor(0,1)
    lcd.printout(value)


setupLCD()
sleep(2)
while True:
    onboard_led.toggle()
    moisture = (max_moisture-soil.read_u16())*100/(max_moisture-min_moisture)
    print("moisture: " + "%.2f" % moisture +"% (adc: "+str(soil.read_u16())+")")
    moisture_percent = "%.2f" % moisture +"%" 
    updateLCD(moisture_percent)
    
    sleep(readDelay)