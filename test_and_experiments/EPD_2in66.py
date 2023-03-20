from machine import Pin, SPI
import framebuf
import utime

# Display resolution
# WIDTH       = 152
# HEIGHT      = 296

# RST_PIN         = 12
# DC_PIN          = 8
# CS_PIN          = 9
# BUSY_PIN        = 13


WF_PARTIAL_2IN66 =[
0x00,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x80,0x80,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x40,0x40,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x80,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x01,0x00,0x00,
0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x22,0x22,0x22,0x22,0x22,0x22,
0x00,0x00,0x00,0x22,0x17,0x41,0xB0,0x32,0x36,
]

class EPD(framebuf.FrameBuffer):
    def __init__(self, width, height, reset, dc, cs, busy):
        self.reset_pin = Pin(reset, Pin.OUT)
        self.busy_pin = Pin(busy, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(cs, Pin.OUT)
        self.width = width
        self.height = height
        self.lut = WF_PARTIAL_2IN66
        

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(dc, Pin.OUT)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init(0)

    # Hardware reset
    def reset(self):
        self.reset_pin(1)
        utime.sleep_ms(200) 
        self.reset_pin(0)
        utime.sleep_ms(200)
        self.reset_pin(1)
        utime.sleep_ms(200)   

    def send_command(self, command):
        self.cs_pin(1)
        self.dc_pin(0)
        self.cs_pin(0)
        self.spi.write(bytearray([command]))
        self.cs_pin(1)

    def send_data(self, data):
        self.cs_pin(1)
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(bytearray([data]))
        self.cs_pin(1)
        
    def ReadBusy(self):
        print('e-Paper busy')
        utime.sleep_ms(100)   
        while(self.busy_pin.value() == 1):      # 0: idle, 1: busy
            utime.sleep_ms(100)    
        print('e-Paper busy release')
        utime.sleep_ms(100)  
        
    def TurnOnDisplay(self):
        self.send_command(0x20)        
        self.ReadBusy()
        
    def SendLut(self):
        self.send_command(0x32)
        for i in range(0, 153):
            self.send_data(self.lut[i])
        self.ReadBusy()
    
    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
    
    def init(self, mode):
        
        self.reset()
         
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()
        
        self.send_command(0x11)
        self.send_data(0x03)
        
        self.SetWindow(8, 0, self.width, self.height)
   
        if(mode == 0):
            self.send_command(0x3c)
            self.send_data(0x01)
        elif(mode == 1):
            self.SendLut()
            self.send_command(0x37) # set display option, these setting turn on previous function
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)  
            self.send_data(0x40)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x3C)
            self.send_data(0x80)

            self.send_command(0x22)
            self.send_data(0xcf)
            
            self.send_command(0x20)
            self.ReadBusy()
            
        else: 
            print("There is no such mode")
    
    def display(self, image):
        if image is None:
            return            
            
        self.SetCursor(1, 295)
        
        self.send_command(0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
        self.TurnOnDisplay()
    
    
    def Clear(self, color):
        self.send_command(0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(color)
        self.TurnOnDisplay()
    
    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
