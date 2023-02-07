#
# Temperature Logger - written by Dorian Wiskow January 2021
#
from machine import Pin, ADC
from utime import time, localtime, sleep
from select import select
from sys import stdin

TEMP_READING_INTERVAL = 30        # read samples every n seconds (1-30, or 60)
FLUSH_LOG_INTERVAL    = 15        # flush (i.e. write samples to flash memory) file every n minutes (1-30, or 60)

timeDelta = 0
year,month,day,hour,minute,second,wday,yday = 0,0,0,0,0,0,0,0

def timeNow(timeDelta):
    return (time() + timeDelta)

def checkTimeSyncUSB(timeDelta):
    ch, buffer = '',''
    while stdin in select([stdin], [], [], 0)[0]:
        ch = stdin.read(1)
        buffer = buffer+ch
    if buffer:
        for i in range(len(buffer)):
            if buffer[i] == 'T':
                break
        buffer = buffer[i:]
        if buffer[:1] == 'T':
            if buffer[1:11].isdigit():
                syncTime = int(buffer[1:11])
                if syncTime > 1609459201: # Thursday 1st January 2021 00:00:01
                    timeDelta = syncTime - int(time())
                else:
                    syncTime = 0
    return timeDelta

sensor_temp = ADC(4)
conversion_factor = 3.3 / (65535)

LED_ONBOARD         = 25                # GP25 (Pico on-board LED)
VBUS_POWER          = 24                # GP24 (USB or battery power indicator)
led_onboard = Pin(LED_ONBOARD, Pin.OUT)
USBpower = Pin(VBUS_POWER, Pin.IN)

logging = False
lastTime = timeNow(timeDelta)

while True:
    timeDelta = checkTimeSyncUSB(timeDelta)        
    correctedRTC = timeNow(timeDelta)

    if correctedRTC != lastTime:
        lastTime = correctedRTC
        
        if timeDelta == 0:
            for i in range(5):
                led_onboard.toggle()
                sleep(0.03)
            led_onboard.value(0)

        (year,month,day,hour,minute,second,wday,yday)=localtime(correctedRTC)
        correctedRTCstring="%d-%02d-%02d %02d:%02d:%02d" % (year,month,day,hour,minute,second)
     
        if USBpower() != 1:
            if logging == False:
                f = open('temperature.log', 'a+t')
                f.write('Time,Temperature'+'\n')
                logging = True

        if logging:

            if (second % TEMP_READING_INTERVAL) == 0:
                reading = sensor_temp.read_u16() * conversion_factor
                temperature = round(27 - ((reading - 0.706)/0.00172), 1)
                f.write(correctedRTCstring+','+str(temperature)+'\n')
                led_onboard.toggle()
                sleep(0.01)
                led_onboard.value(0)

            if (minute % FLUSH_LOG_INTERVAL) == 0 and second == 0:
                f.flush()
                for i in range(9):
                    led_onboard.toggle()
                    sleep(0.03)
                led_onboard.value(0)