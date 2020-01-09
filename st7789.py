import time
import ustruct as struct
import framebuf
from micropython import const
from machine import SPI


TFT_RAMWR = const(0x2C)
TFT_SWRST = const(0x01)
ST7789_SLPOUT = const(0x11)
ST7789_NORON = const(0x13)

TFT_MAD_COLOR_ORDER = const(0x08)
ST7789_COLMOD = const(0x3A)
ST7789_PORCTRL = const(0xB2)
ST7789_GCTRL = const(0xB7)
ST7789_VCOMS = const(0xBB)
ST7789_LCMCTRL = const(0xC0)
ST7789_VDVVRHEN = const(0xC2)
ST7789_VRHS = const(0xC3)
ST7789_VDVSET = const(0xC4)
ST7789_FRCTR2 = const(0xC6)
ST7789_PWCTRL1 = const(0xD0)
ST7789_PVGAMCTRL = const(0xD0)
ST7789_NVGAMCTRL = const(0xE1)
ST7789_INVON = const(0x21)
ST7789_CASET = const(0x2A)
ST7789_RASET = const(0x2B)
ST7789_DISPON = const(0x29)
ST7789_DISPOFF = const(0x28)


# commands
ST77XX_NOP = const(0x00)
ST77XX_SWRESET = const(0x01)
ST77XX_RDDID = const(0x04)
ST77XX_RDDST = const(0x09)
ST77XX_SLPIN = const(0x10)
ST77XX_SLPOUT = const(0x11)
ST77XX_PTLON = const(0x12)
ST77XX_NORON = const(0x13)
ST77XX_INVOFF = const(0x20)
ST77XX_INVON = const(0x21)
ST77XX_CASET = const(0x2A)
ST77XX_RASET = const(0x2B)
ST77XX_RAMWR = const(0x2C)
ST77XX_RAMRD = const(0x2E)
ST77XX_PTLAR = const(0x30)
ST7789_MADCTL = const(0x36)
ST7789_MADCTL_MY = const(0x80)
ST7789_MADCTL_MX = const(0x40)
ST7789_MADCTL_MV = const(0x20)
ST7789_MADCTL_ML = const(0x10)
ST7789_MADCTL_BGR = const(0x08)
ST7789_MADCTL_MH = const(0x04)
ST7789_MADCTL_RGB = const(0x00)

ST7789_RDID1 = const(0xDA)
ST7789_RDID2 = const(0xDB)
ST7789_RDID3 = const(0xDC)
ST7789_RDID4 = const(0xDD)

ColorMode_65K = const(0x50)
ColorMode_262K = const(0x60)
ColorMode_12bit = const(0x03)
ColorMode_16bit = const(0x05)
ColorMode_18bit = const(0x06)
ColorMode_16M = const(0x07)

# Color definitions
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_ENCODE_PIXEL = ">H"
_ENCODE_POS = ">HH"
_DECODE_PIXEL = ">BBB"

_BUFFER_SIZE = const(256)


def delay_ms(ms):
    time.sleep_ms(ms)


def color565(r, g=0, b=0):
    """Convert red, green and blue values (0-255) into a 16-bit 565 encoding.  As
    a convenience this is also available in the parent adafruit_rgb_display
    package namespace."""
    try:
        r, g, b = r  # see if the first var is a tuple/list
    except TypeError:
        pass
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3


class ST7789(object):
    def __init__(self, spi, width, height, rst, dc, cs, backlight=None,
                 xstart=-1, ystart=-1):
        """
        display = st7789.ST7789(
            SPI(baudrate=40000000, miso=Pin(x), mosi=Pin(y, Pin.OUT), sck=Pin(z, Pin.OUT) ),
            240, 240,
            reset=machine.Pin(23, machine.Pin.OUT),
            dc=machine.Pin(16, machine.Pin.OUT),
        )

        """
        self.width = width
        self.height = height
        self.spi = spi

        self.rst = rst
        self.dc = dc
        self.cs = cs
        self.backlight = backlight

        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        if self.rst is not None:
            self.rst.init(self.rst.OUT, value=0)

        self._buf = bytearray(_BUFFER_SIZE * 2)
        # default white foregraound, black background
        self._colormap = bytearray(b'\x00\x00\xFF\xFF')

        if xstart >= 0 and ystart >= 0:
            self.xstart = xstart
            self.ystart = ystart
        elif (self.width, self.height) == (240, 240):
            self.xstart = 0
            self.ystart = 0
        elif (self.width, self.height) == (135, 240):
            self.xstart = 52
            self.ystart = 40
        else:
            raise ValueError(
                "Unsupported display. Only 240x240 and 135x240 are supported "
                "without xstart and ystart provided"
            )

        self.init_pins()
        if self.rst is not None:
             self.reset()
        else:
             self.soft_reset()
        self.init()

    def reset(self):
         self.rst(0)
         time.sleep(0.5)
         self.rst(1)
         time.sleep(0.5)

    def init_pins(self):
         pass


    def dc_low(self):
        self.dc.off()


    def dc_high(self):
        self.dc.on()


    def reset_low(self):
        if self.rst:
            self.rst.off()


    def reset_high(self):
        if self.rst:
            self.rst.on()


    def cs_low(self):
        if self.cs:
            self.cs.off()


    def cs_high(self):
        if self.cs:
            self.cs.on()


    def write(self, command, data=None):
        """SPI write to the device: commands and data"""
        self.dc_low()
        self.cs_low()
        if command is not None:
            self.spi.write(bytearray([command]))
        self.cs_high()
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc_high()
        self.cs_low()
        if type(data) == type(1):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs_high()

    def hard_reset(self):
        self.reset_low()
        time.sleep(0.5)
        self.reset_high()
        time.sleep(0.5)

    def soft_reset(self):
        self.write(ST77XX_SWRESET)
        time.sleep(0.5)

    def sleep_mode(self, value):
        if value:
            self.write(ST77XX_SLPIN)
        else:
            self.write(ST77XX_SLPOUT)

    def inversion_mode(self, value):
        if value:
            self.write(ST77XX_INVON)
        else:
            self.write(ST77XX_INVOFF)

    def _set_color_mode(self, mode):
        self.write(ST7789_COLMOD, bytes([mode & 0x77]))

    def init(self):
        self.write(ST7789_SLPOUT)   # Sleep out
        time.sleep_ms(120)

        self.write(ST7789_NORON)    # Normal display mode on

        #------------------------------display and color format setting--------------------------------#
        self.write(ST7789_MADCTL)
        # self._data(0x00)
        self._data(TFT_MAD_COLOR_ORDER)

        # JLX240 display datasheet
        self.write(0xB6)
        self._data(0x0A)
        self._data(0x82)

        self.write(ST7789_COLMOD)
        self._data(0x55)
        time.sleep_ms(10)

        #--------------------------------ST7789V Frame rate setting----------------------------------#
        self.write(ST7789_PORCTRL)
        self._data(0x0c)
        self._data(0x0c)
        self._data(0x00)
        self._data(0x33)
        self._data(0x33)

        self.write(ST7789_GCTRL)      # Voltages: VGH / VGL
        self._data(0x35)

        #---------------------------------ST7789V Power setting--------------------------------------#
        self.write(ST7789_VCOMS)
        self._data(0x28)        # JLX240 display datasheet

        self.write(ST7789_LCMCTRL)
        self._data(0x0C)

        self.write(ST7789_VDVVRHEN)
        self._data(0x01)
        self._data(0xFF)

        self.write(ST7789_VRHS)       # voltage VRHS
        self._data(0x10)

        self.write(ST7789_VDVSET)
        self._data(0x20)

        self.write(ST7789_FRCTR2)
        self._data(0x0f)

        self.write(ST7789_PWCTRL1)
        self._data(0xa4)
        self._data(0xa1)

        #--------------------------------ST7789V gamma setting---------------------------------------#
        self.write(ST7789_PVGAMCTRL)
        self._data(0xd0)
        self._data(0x00)
        self._data(0x02)
        self._data(0x07)
        self._data(0x0a)
        self._data(0x28)
        self._data(0x32)
        self._data(0x44)
        self._data(0x42)
        self._data(0x06)
        self._data(0x0e)
        self._data(0x12)
        self._data(0x14)
        self._data(0x17)

        self.write(ST7789_NVGAMCTRL)
        self._data(0xd0)
        self._data(0x00)
        self._data(0x02)
        self._data(0x07)
        self._data(0x0a)
        self._data(0x28)
        self._data(0x31)
        self._data(0x54)
        self._data(0x47)
        self._data(0x0e)
        self._data(0x1c)
        self._data(0x17)
        self._data(0x1b)
        self._data(0x1e)

        self.write(ST7789_INVON)

        self.write(ST7789_CASET)    # Column address set
        self._data(0x00)
        self._data(0x00)
        self._data(0x00)
        self._data(0xE5)    # 239

        self.write(ST7789_RASET)    # Row address set
        self._data(0x00)
        self._data(0x00)
        self._data(0x01)
        self._data(0x3F)    # 319

        # /

        time.sleep_ms(120)

        self.write(ST7789_DISPON)  # Display on
        time.sleep_ms(120)




    def _set_mem_access_mode(self, rotation, vert_mirror, horz_mirror, is_bgr):
        rotation &= 7
        value = {
            0: 0,
            1: ST7789_MADCTL_MX,
            2: ST7789_MADCTL_MY,
            3: ST7789_MADCTL_MX | ST7789_MADCTL_MY,
            4: ST7789_MADCTL_MV,
            5: ST7789_MADCTL_MV | ST7789_MADCTL_MX,
            6: ST7789_MADCTL_MV | ST7789_MADCTL_MY,
            7: ST7789_MADCTL_MV | ST7789_MADCTL_MX | ST7789_MADCTL_MY,
        }[rotation]

        if vert_mirror:
            value = ST7789_MADCTL_ML
        elif horz_mirror:
            value = ST7789_MADCTL_MH

        if is_bgr:
            value |= ST7789_MADCTL_BGR
        self.write(ST7789_MADCTL, bytes([value]))

    def _encode_pos(self, x, y):
        """Encode a postion into bytes."""
        return struct.pack(_ENCODE_POS, x, y)

    def _encode_pixel(self, color):
        """Encode a pixel color into bytes."""
        return struct.pack(_ENCODE_PIXEL, color)

    def vline(self, x, y, length, color):
        self.fill_rect(x, y, 1, length, color)

    def hline(self, x, y, length, color):
        self.fill_rect(x, y, length, 1, color)

    def pixel(self, x, y, color):
        self.set_window(x, y, x, y)
        self.write(None, self._encode_pixel(color))

    def blit_buffer(self, buffer, x, y, width, height):
        self.set_window(x, y, x + width - 1, y + height - 1)
        self.write(None, buffer)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
        self.hline(x, y + h - 1, w, color)

    def _set_columns(self, start, end):
        if start > end or end >= self.width:
            return
        start += self.xstart
        end += self.xstart
        self.write(ST7789_CASET, self._encode_pos(start, end))

    def _set_rows(self, start, end):
        if start > end or end >= self.height:
            return
        start += self.ystart
        end += self.ystart
        self.write(ST7789_RASET, self._encode_pos(start, end))


    def set_window(self, x0, y0, x1, y1, data=None):
        self._set_columns(x0, x1)
        self._set_rows(y0, y1)
        self.write(ST77XX_RAMWR, data)


    def fill_rect(self, x, y, width, height, color):
        if color:
           pixel = self._encode_pixel(color)
        else:
           pixel = self._colormap[0:2]  # background

        for i in range(_BUFFER_SIZE):
            self._buf[2*i] = pixel[0]
            self._buf[2*i+1] = pixel[1]
        chunks, rest = divmod(width * height, _BUFFER_SIZE)

        self.set_window(x, y, x + width - 1, y + height - 1)

        if chunks:
            for _ in range(chunks):
                self._data(self._buf)
        if rest != 0:
            mv = memoryview(self._buf)
            self._data(mv[:rest*2])


    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)


    def line(self, x0, y0, x1, y1, color):
        # Line drawing function.  Will draw a single pixel wide line starting at
        # x0, y0 and ending at x1, y1.
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        if y0 < y1:
            ystep = 1
        else:
            ystep = -1
        while x0 <= x1:
            if steep:
                self.pixel(y0, x0, color)
            else:
                self.pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1
