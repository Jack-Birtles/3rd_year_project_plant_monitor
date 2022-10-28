from network import WLAN, STA_IF
from time import sleep
from rp2 import country

# set wireless driver to use correct settings if needed
country("GB")

ssid = "VM3345192"
password = "zgnd5RvGdnxn"

# convert values from wlan.status()
status_values = ["LINK_DOWN", "LINK_JOIN", "LINK_NOIP", "LINK_UP", "LINK_FAIL", "LINK_NONET", "LINK_BADAUTH"]

wlan = WLAN(STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# wait for connection (time in seconds)
wait_time = 10
while wait_time > 0:
    if 0 > wlan.status() >= 3:
        break
    wait_time -= 1
    print("waiting for connection")
    sleep(1)
    
# handle failure to connect
if wlan.status() != 3:
    print(status_values[wlan.status()])
    raise RuntimeError("network connection failed")
else:
    print("connected")
    print(status_values[wlan.status()])
    status = wlan.ifconfig()
    print("ip = " + status[0])