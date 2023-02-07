# Library for Adafruit TSL2561 lux sensor
# Originally by Carter Nelson, rewritten for MicroPython by Jack Birtles

from machine import Pin, I2C

_DEFAULT_FREQ = 400000

_DEFAULT_ADDRESS = 0x39
_COMMAND_BIT = 0x80
_WORD_BIT = 0x20

_CONTROL_POWERON = 0x03
_CONTROL_POWEROFF = 0x00

_REGISTER_CONTROL = 0x00
_REGISTER_TIMING = 0x01
_REGISTER_TH_LOW = 0x02
_REGISTER_TH_HIGH = 0x04
_REGISTER_INT_CTRL = 0x06
_REGISTER_CHAN0_LOW = 0x0C
_REGISTER_CHAN1_LOW = 0x0E
_REGISTER_ID = 0x0A

_GAIN_SCALE = (16, 1)
_TIME_SCALE = (1 / 0.034, 1 / 0.252, 1)
_CLIP_THRESHOLD = (4900, 37000, 65000)


class TSL2561:
    # Provides interface to TSL2561 light sensor
    
    def __init__(self, port: int, SDA: Pin, SCL: Pin, FREQ: int = _DEFAULT_FREQ) -> None:
        self.buf = bytearray(3)
        self.TSL2561_I2C = I2C(port, sda = SDA, scl = SCL, freq = FREQ)
        self.enabled = True
        
    @property
    def enabled(self) -> bool:
        # Current state of the sensor
        return (self._read_register(_REGISTER_CONTROL) & 0x03) != 0
    
    
    @enabled.setter
    def enabled(self, enable: bool) -> None:
        # Enable or disable the sensor
        if enable:
            self._enable()
        else:
            self._disable()
            
    @property
    def lux(self) -> Optional[float]:
        # The computed lux value or None when value is not computable
        return self._compute_lux()

    @property
    def broadband(self) -> int:
        # The broadband channel value
        return self._read_broadband()

    @property
    def infrared(self) -> int:
        # The infrared channel value
        return self._read_infrared()

    @property
    def luminosity(self) -> Tuple[int, int]:
        # The overall luminosity as a tuple containing the broadband
        # channel and the infrared channel value
        return (self.broadband, self.infrared)

    @property
    def gain(self) -> int:
        """The gain. 0:1x, 1:16x."""
        return self._read_register(_REGISTER_TIMING) >> 4 & 0x01
    
    @gain.setter
    def gain(self, value: int) -> None:
        # Set the gain. 0:1x, 1:16x
        value &= 0x01
        value <<= 4
        current = self._read_register(_REGISTER_TIMING)
        self.buf[0] = _COMMAND_BIT | _REGISTER_TIMING
        self.buf[1] = (current & 0xEF) | value
        self.TSL2561_I2C.write(self.buf, end=2)