from network import WLAN, STA_IF


class webserver:
    """_summary_
    """
    
    def __init__(self, network) -> None:
        self.ssid = network["name"]
        self.password = network["password"]

    def connect(self) -> bool:
        status_values = ["LINK_DOWN", "LINK_JOIN", "LINK_NOIP", "LINK_UP",
                        "LINK_FAIL", "LINK_NONET", "LINK_BADAUTH"]

        wlan = WLAN(STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)

        wait_time = 10
        while wait_time > 0:
            if 0 > wlan.status() >= 3:
                break
            wait_time -= 1
            print("Connecting...")
            sleep(1)

        if wlan.status() != 3:
            print(status_values[wlan.status()])
            # raise RuntimeError("network connection failed")
            return False

        print("connected")
        print(status_values[wlan.status()])
        status = wlan.ifconfig()
        print("ip = " + status[0])
        
        return True

    def getWebpage(file):
        try:
            with open(file, "r") as f:
                page = f.read()
        except Exception as e:
            print(e, "\nfile does not exist")
            raise e

        return page

    def serveClient(reader, writer):
        page = getWebpage("index.html")


        print("client connected")
        request_line = await reader.readline()
        print("request: ", request_line)

        while await reader.readline() != b"\r\n":
            pass

        # request = str(request_line)


        response = page
        response = response.replace("moistureValue", sensor_averages["moisture"])
        response = response.replace("temperatureValue", sensor_averages["temperature"])
        response = response.replace("humidityValue", sensor_averages["humidity"])
        response = response.replace("lightValue", sensor_averages["light"])
        writer.write("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        writer.write(response)

        await writer.drain()
        await writer.wait_closed()
        print("client disconnecting")