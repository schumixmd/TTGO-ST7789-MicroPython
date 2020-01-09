
from machine import Pin, SPI
from random import random, seed
from st7789 import ST7789, color565
from utime import sleep_us, ticks_cpu, ticks_us, ticks_diff


class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, display, color):
        """Initialize box.

        Args:
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            display (SSD1351): OLED display object.
            color (int): RGB565 color value.
        """
        self.size = size
        self.w = screen_width
        self.h = screen_height
        self.display = display
        self.color = color
        # Generate non-zero random speeds between -5.0 and 5.0
        seed(ticks_cpu())
        r = random() * 10.0
        self.x_speed = 5.0 - r if r < 5.0 else r - 10.0
        r = random() * 10.0
        self.y_speed = 5.0 - r if r < 5.0 else r - 10.0

        self.x = self.w / 2.0
        self.y = self.h / 2.0
        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update box position and speed."""
        x = self.x
        y = self.y
        size = self.size
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)
        self.prev_x = x
        self.prev_y = y

        if x + size >= w - x_speed:
            self.x_speed = -x_speed
        elif x - size <= x_speed + 1:
            self.x_speed = x_speed

        if y + size >= h - y_speed:
            self.y_speed = -y_speed
        elif y - size <= y_speed + 1:
            self.y_speed = y_speed

        self.x = x + self.x_speed
        self.y = y + self.y_speed

    def draw(self):
        """Draw box."""
        x = int(self.x)
        y = int(self.y)
        size = self.size
        prev_x = int(self.prev_x)
        prev_y = int(self.prev_y)
        self.display.fill_hrect(prev_x - size,
                                prev_y - size,
                                size, size, 0)
        self.display.fill_hrect(x - size,
                                y - size,
                                size, size, self.color)


def test():
    """Bouncing box."""
    try:
        # Baud rate of 14500000 seems about the max
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
        display = ST7789(spi, 135, 240, cs=Pin(CS_Pin), dc=Pin(DC_Pin), rst=None)
        display.fill(0)

        colors = [color565(255, 0, 0),
                  color565(0, 255, 0),
                  color565(0, 0, 255),
                  color565(255, 255, 0),
                  color565(0, 255, 255),
                  color565(255, 0, 255)]
        sizes = [12, 11, 10, 9, 8, 7]
        boxes = [Box(135, 240, sizes[i], display,
                 colors[i]) for i in range(6)]

        while True:
            timer = ticks_us()
            for b in boxes:
                b.update_pos()
                b.draw()
            # Attempt to set framerate to 30 FPS
            timer_dif = 33333 - ticks_diff(ticks_us(), timer)
            if timer_dif > 0:
                sleep_us(timer_dif)

    except KeyboardInterrupt:
        display.cleanup()


test()
