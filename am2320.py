# Jack Birtles
# Last updated 23/03/23
#
# A micropython driver for the AOSONG AM2320 temperature and humidity
# sensor. Based on the Adafruit circuitpython driver :
# https://github.com/adafruit/Adafruit_CircuitPython_AM2320
# SPDX-FileCopyrightText: 2018 Limor Fried for Adafruit Industries
# SPDX-License-Identifier: MIT
#


import time
import ustruct

default_addr = 0x5C
read_reg = 0x03
temp_reg = 0x02
hum_reg = 0x00


class AM2320:
    """
    Driver for an AM2320 sensor

    Attributes:
        i2c (I2C): object to communicate with the sensor over i2c
        address (Literal): address of the sensor
    """
    def __init__(self, i2c, address: int = default_addr):
        self.i2c = i2c
        self.address = address

    def _read_register(self, register: int) -> bytearray:
        """
        Sends a read command to the sensor, reads the data and performs a cyclic redundancy check

        Args:
            register (int): register address

        Raises:
            RuntimeError: raised on CRC failure of the read data

        Returns:
            bytearray: binary data received from the sensor
        """
        # wake sensor up
        try:
            self.i2c.writeto(self.address, b"0x00")
        except OSError:
            pass

        time.sleep_ms(10)

        # read register command
        cmd = [read_reg, register & 0xFF, 2]
        self.i2c.writeto(self.address, bytes(cmd))
        time.sleep_ms(2)
        # read data 
        result = bytearray(6)
        self.i2c.readfrom_mem_into(self.address, 0, result)

        # check crc
        crc1 = ustruct.unpack("<H", bytearray(result[-2:]))[0]
        crc2 = self._crc16(result[:-2])
        if crc1 != crc2:
            raise RuntimeError("CRC failure 0x%04X vs 0x%04X" % (crc1, crc2))

        return result[2:-2]

    def _crc16(self, data: bytearray) -> int:
        """
        Checks the given bytearray through a 16-bit crc checksum

        Args:
            data (bytearray): bytearray read from the sensor

        Returns:
            int: 16-bit checksum
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for i in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def temperature(self) -> float:
        """
        Convert the measured value into celsius

        Returns:
            float: temperature in celsius
        """
        raw_value = self._read_register(temp_reg)
        temperature = ustruct.unpack(">H", raw_value)[0]
        if temperature >= 32768:
            temperature = -temperature
        return temperature / 10

    def humidity(self) -> float:
        """
        Convert the measured relative humidity into percent

        Returns:
            float: relative humidity
        """
        raw_value = self._read_register(hum_reg)
        humidity = ustruct.unpack(">H", raw_value)[0]
        return humidity / 10
