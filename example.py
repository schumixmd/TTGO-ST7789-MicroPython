
import random
import st7789
import time
from machine import Pin, SPI

BL_Pin = 4     #backlight pin
SCLK_Pin = 18  #clock pin
MOSI_Pin = 19  #mosi pin
MISO_Pin = 2   #miso pin
RESET_Pin = 23 #reset pin
DC_Pin = 16    #data/command pin
CS_Pin = 5     #chip select pin

Button1_Pin = 35; #right button
Button2_Pin = 0;  #left button
button1 = Pin(Button1_Pin, Pin.IN, Pin.PULL_UP)
button2 = Pin(Button2_Pin, Pin.IN, Pin.PULL_UP)

BLK = Pin(BL_Pin, Pin.OUT)
spi = SPI(baudrate=40000000, miso=Pin(MISO_Pin), mosi=Pin(MOSI_Pin, Pin.OUT), sck=Pin(SCLK_Pin, Pin.OUT))
display = st7789.ST7789(spi, 135, 240, cs=Pin(CS_Pin), dc=Pin(DC_Pin), rst=None)

def clear_screen():
    display.fill(0);

def fill_random_color():
    display.fill(
      st7789.color565(
          random.getrandbits(8),
          random.getrandbits(8),
          random.getrandbits(8),
      ),
    )

def fill_hline():
    display._set_mem_access_mode(0, False, False, False)
    for i in range(0,240):
      display.hline(0, i, 65, st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

    display._set_mem_access_mode(1, False, False, False)
    for i in range(0,240):
      display.hline(0, i, 65, st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

    clear_screen()

def fill_vline():
    display._set_mem_access_mode(0, False, False, False)
    for i in range(0,135):
      display.vline(i, 0, 110, st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

    display._set_mem_access_mode(2, False, False, False)
    for i in range(0,135):
      display.vline(i, 0, 110, st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))




    clear_screen()

def random_color():
    return st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

def main():

  BLK.value(1) #turn backlight on
  display._set_mem_access_mode(0, False, False, True) #setting screen orientation (rotation (0-7), vertical mirror, horizonatal mirror, is bgr)
  clear_screen() #clear screen by filling black rectangle (slow)


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
    display.circle(x,y,30,random_color())
    display.ellipse(x, y, 10, 20, random_color())
     #display.line(x, y, w, h, st7789.color565(
    #     random.getrandbits(8),
    #     random.getrandbits(8),
    #     random.getrandbits(8),
     #))

     #display.rect(50, 50, 50, 50, st7789.WHITE)

    clear_screen()
    time.sleep(1)

    clear_screen()

    display.hline(10, 127, 63, st7789.color565(255, 0, 255))
    time.sleep(1)

    display.vline(10, 0, 127, st7789.color565(0, 255, 255))
    time.sleep(1)

    display.fill_hrect(23, 50, 30, 75, st7789.color565(255, 255, 255))
    time.sleep(1)

    display.hline(0, 0, 127, st7789.color565(255, 0, 0))
    time.sleep(1)

    display.line(127, 0, 64, 127, st7789.color565(255, 255, 0))
    time.sleep(2)

    clear_screen()

    coords = [[0, 63], [78, 80], [122, 92], [50, 50], [78, 15], [0, 63]]
    display.lines(coords, st7789.color565(0, 255, 255))
    time.sleep(1)

    clear_screen()
    display.fill_polygon(7, 63, 63, 50, st7789.color565(0, 255, 0))
    time.sleep(1)

    display.fill_rectangle(0, 0, 15, 127, st7789.color565(255, 0, 0))
    time.sleep(1)

    clear_screen()

    display.fill_rectangle(0, 0, 63, 63, st7789.color565(128, 128, 255))
    time.sleep(1)

    display.rectangle(0, 64, 63, 63, st7789.color565(255, 0, 255))
    time.sleep(1)

    display.fill_rectangle(64, 0, 63, 63, st7789.color565(128, 0, 255))
    time.sleep(1)

    display.polygon(3, 96, 96, 30, st7789.color565(0, 64, 255),
                         rotate=15)
    time.sleep(3)

    clear_screen()

    display.fill_circle(32, 32, 30, st7789.color565(0, 255, 0))
    time.sleep(1)

    display.circle(32, 96, 30, st7789.color565(0, 0, 255))
    time.sleep(1)

    display.fill_ellipse(96, 32, 30, 16, st7789.color565(255, 0, 0))
    time.sleep(1)

    display.ellipse(96, 96, 16, 30, st7789.color565(255, 255, 0))



main()
