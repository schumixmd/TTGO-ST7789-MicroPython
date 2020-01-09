
import random
import st7789
import time
from machine import Pin, SPI

BL_Pin = 4     #Backlight pin
SCLK_Pin = 18  #Clock
MOSI_Pin = 19  #MOSI
MISO_Pin = 2   #MISO
RESET_Pin = 23 #RESET
DC_Pin = 16    #Data/Command Select
CS_Pin = 5     #Chip Select

Button1_Pin = 35 #Right button
Button2_Pin = 0  #Left button
button1 = Pin(Button1_Pin, Pin.IN, Pin.PULL_UP)
button2 = Pin(Button2_Pin, Pin.IN, Pin.PULL_UP)

BLK = Pin(BL_Pin, Pin.OUT)
spi = SPI(baudrate=40000000, miso=Pin(MISO_Pin), mosi=Pin(MOSI_Pin, Pin.OUT), sck=Pin(SCLK_Pin, Pin.OUT))
display = st7789.ST7789(spi, 135, 240, cs=Pin(CS_Pin), dc=Pin(DC_Pin), rst=None)

def clear_screen():
    display.fill(st7789.BLACK)

def fill_random_color():
    display.fill(
      st7789.color565(
          random.getrandbits(8),
          random.getrandbits(8),
          random.getrandbits(8),
      ),
    )

def fill_hline():
    for i in range(0,240):
      display.hline(0, i, 135, st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

def fill_vline():
    for i in range(0,135):
      display.vline(i, 0, 240, st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

def main():

    BLK.value(1) #turn backlight on
    display.fill(st7789.BLACK) #clear screen by filling all black

    while True:
     if not button1.value():
        fill_hline()
     if not button2.value():
        fill_vline()

     #display.fill(st7789.BLACK)
     #display.pixel(random.randint(0, 135), random.randint(0, 240) , st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))
     #display.vline(70, 0, 135, st7789.BLUE)
     #display.hline(20, 70, 100, st7789.RED)
     x = random.randint(0,135)
     y = random.randint(0,240)
     w = random.randint(0,135)
     h = random.randint(0,240)

     display.line(x, y, w, h, st7789.color565(
         random.getrandbits(8),
         random.getrandbits(8),
         random.getrandbits(8),
     ))

     #display.rect(50, 50, 50, 50, st7789.WHITE)

    
