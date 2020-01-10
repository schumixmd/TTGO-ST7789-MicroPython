from time import sleep
from st7789 import ST7789, color565
from machine import Pin, SPI
import random




def random_color():
    return color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

def test():
    """Test code."""
    # Baud rate of 14500000 seems about the max
    blk = Pin(4, Pin.OUT)
    spi = SPI(baudrate=40000000, miso=Pin(2), mosi=Pin(19, Pin.OUT), sck=Pin(18, Pin.OUT))
    display = ST7789(spi, 135, 240, cs=Pin(5), dc=Pin(16), rst=None)
    blk.value(1)


    for x in range(0, 134, 15):
        for y in range(0, 239, 15):
            display.fill_rectangle(x, y, 15, 15, random_color())

    sleep(9)
    display.cleanup()


test()
