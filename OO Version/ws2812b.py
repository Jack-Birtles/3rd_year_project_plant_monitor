import array
from time import sleep_ms
from machine import Pin
from rp2 import asm_pio, StateMachine, PIO


@asm_pio(sideset_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)              .side(0)  [T3 - 1]
    jmp(not_x, "do_zero")  .side(1)  [T1 - 1]
    jmp("bitloop")         .side(1)  [T2 - 1]
    label("do_zero")
    nop()                  .side(0)  [T2 - 1]
    wrap()


class Neopixel_Controller:

    def __init__(self, pin, led_count) -> None:
        self.led_count = led_count
        self.state_machine = StateMachine(0, ws2812, freq=8000000, sideset_base=Pin(pin))
        self.state_machine.active(1)

    def fill(self, color, brightness):
        dimmer_ar = array.array("I", [0 for _ in range(self.led_count)])

        for i in range(self.led_count):
            r = int((color[1] & 0xFF) * brightness)
            g = int((color[0] & 0xFF) * brightness)
            b = int((color[2] & 0xFF) * brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b

        self.state_machine.put(dimmer_ar, 8)
        sleep_ms(10)
