from time import sleep
from st7789 import ST7789
from machine import Pin, SPI

BL_Pin = 4     #backlight pin
SCLK_Pin = 18  #clock pin
MOSI_Pin = 19  #mosi pin
MISO_Pin = 2   #miso pin
RESET_Pin = 23 #reset pin
DC_Pin = 16    #data/command pin
CS_Pin = 5     #chip select pin

def test():
    """Test code."""
    BLK = Pin(BL_Pin, Pin.OUT)
    spi = SPI(baudrate=40000000, miso=Pin(MISO_Pin), mosi=Pin(MOSI_Pin, Pin.OUT), sck=Pin(SCLK_Pin, Pin.OUT))
    display = ST7789(spi, 135, 240, cs=Pin(CS_Pin), dc=Pin(DC_Pin), rst=None)
    BLK.value(1)

    display.draw_image('images/RaspberryPiWB128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/MicroPython128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/MicroPythonW128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/Tabby128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/Rototron128x26.raw', 0, 0, 128, 26)
    sleep(5)

    display.draw_image('images/Tortie128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/Python41x49.raw', 0, 0, 41, 49)
    sleep(5)

    display.draw_image('images/Mario13x96.raw', 0, 0, 13, 96)
    sleep(5)


    display.cleanup()


test()
