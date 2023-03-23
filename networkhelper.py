# Jack Birtles
# Last updated 23/03/23
#
# A micropython controller for the Raspberry Pi Pico builtin WiFi module

from network import WLAN, STA_IF
from time import sleep


class networkHelper:
    """
    Handles connecting to a specified WiFi network

    Attributes:
        ssid (string): network name
        password (string): network password
        ip (string): IP address on successful connection
    """

    def __init__(self, network) -> None:
        self.ssid = network["name"]
        self.password = network["password"]
        self.ip = ""

    def connect(self) -> bool:
        """Attempt a connection to the provided network

        Returns:
            bool: True if successful connection
        """

        status_values = ["DOWN", "JOIN", "NOIP", "UP",
                         "FAIL", "NONET", "BADAUTH"]

        wlan = WLAN(STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)

        # If no connection in 10 seconds, give up
        wait_time = 10
        while wait_time > 0:
            if 0 > wlan.status() >= 3:
                break
            wait_time -= 1
            print("connecting")
            sleep(1)

        if wlan.status() != 3:
            print(status_values[wlan.status()])
            # If a connection is not established, provide reason why
            self.ip = status_values[wlan.status()]
            return False

        print("connected")
        print(status_values[wlan.status()])
        status = wlan.ifconfig()
        self.ip = status[0]
        print("ip = " + self.ip)

        return True

    def get_ip(self):
        """Return the current IP address

        Returns:
            int: IP address
        """
        return self.ip

    def get_webpage(self, file):
        """Open and read the provided file as a webpage

        Args:
            file (string): file path

        Returns:
            page: contents of the opened html file
        """
        try:
            with open(file, "r") as f:
                page = f.read()
        except Exception as e:
            print(e, "\nfile does not exist")
            raise e

        return page
