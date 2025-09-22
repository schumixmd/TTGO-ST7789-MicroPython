from time import sleep
from st7789 import ST7789, color565
from machine import Pin, SoftSPI
import random




def random_color():
    return color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

def test():
    """Test code."""
    # Baud rate of 14500000 seems about the max
    blk = Pin(4, Pin.OUT)
    spi = SoftSPI(baudrate=500000, polarity=1, phase=0, sck=Pin(SCLK_Pin), mosi=Pin(MOSI_Pin), miso=Pin(MISO_Pin))
    display = ST7789(spi, 135, 240, cs=Pin(5), dc=Pin(16), rst=None)
    blk.value(1)


    for x in range(0, 134, 15):
        for y in range(0, 239, 15):
            display.fill_rectangle(x, y, 15, 15, random_color())

    sleep(9)
    display.cleanup()


test()
