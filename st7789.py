'''MicroPython Library for ESP32-TTGO-ST7789 Display. Credits: schumixmd
   The library is a mix of multiple functions collected from other libraries.
   Needs a lot of cleanup, but is fully functional, except the Fonts part.
    https://github.com/devbis/st7789py_mpy <-- display initialization
    https://github.com/lewisxhe/mPython_ST7789 <-- basis of this library
    https://github.com/rdagger/micropython-ssd1351 <-- most of the functions including Fonts
    https://github.com/boochow/MicroPython-ST7735 <-- for text using the font sysfont
'''
import time
import ustruct as struct
import framebuf
from micropython import const
from machine import SPI
from math import cos, sin, pi, radians

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
SET_REMAP = const(0xA0)


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

    def cleanup(self):
        """Clean up resources."""
        self.fill(0)
        self.display_off()
        self.spi.deinit()
        print('display off')

    def display_off(self):
        """Turn display off."""
        self.write(ST7789_DISPOFF)

    def display_on(self):
        """Turn display on."""
        self.write(ST7789_DISPON)

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

    def is_off_grid(self, xmin, ymin, xmax, ymax):
        """Check if coordinates extend past display boundaries.

        Args:
            xmin (int): Minimum horizontal pixel.
            ymin (int): Minimum vertical pixel.
            xmax (int): Maximum horizontal pixel.
            ymax (int): Maximum vertical pixel.
        Returns:
            boolean: False = Coordinates OK, True = Error.
        """
        if xmin < 0:
            print('x-coordinate: {0} below minimum of 0.'.format(xmin))
            return True
        if ymin < 0:
            print('y-coordinate: {0} below minimum of 0.'.format(ymin))
            return True
        if xmax >= self.width:
            print('x-coordinate: {0} above maximum of {1}.'.format(
                xmax, self.width - 1))
            return True
        if ymax >= self.height:
            print('y-coordinate: {0} above maximum of {1}.'.format(
                ymax, self.height - 1))
            return True
        return False


    def draw_letter(self, x, y, letter, font, color, background=0,
                    landscape=False):
        """Draw a letter.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            letter (string): Letter to draw.
            font (XglcdFont object): Font.
            color (int): RGB565 color value.
            background (int): RGB565 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
        """
        buf, w, h = font.get_letter(letter, color, background,
                                    landscape)
        # Check for errors
        if w == 0:
            return w, h

        if landscape:
            y -= w
            if self.is_off_grid(x, y, x + h - 1, y + w - 1):
                return
            self.set_window(x, y,
                       x + h - 1, y + w - 1,
                       buf)
        else:
            if self.is_off_grid(x, y, x + w - 1, y + h - 1):
                return

            self.set_window(y, x,
                       y + h - 1,  x + w - 1,
                       buf)

        return w, h

    def draw_text(self, x, y, text, font, color,  background=0,
                  landscape=False, spacing=1):
        """Draw text.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            text (string): Text to draw.
            font (XglcdFont object): Font.
            color (int): RGB565 color value.
            background (int): RGB565 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
            spacing (int): Pixels between letters (default: 1)
        """
        for letter in text:
            # Get letter array and letter dimensions
            w, h = self.draw_letter(x, y, letter, font, color, background,
                                    landscape)
            # Stop on error
            if w == 0 or h == 0:
                print('Invalid width {0} or height {1}'.format(w, h))
                return

            if landscape:
                # Fill in spacing
                if spacing:
                    self.fill_hrect(x, y - w - spacing, h, spacing, background)
                # Position y for next letter
                y -= (w + spacing)
            else:
                # Fill in spacing
                if spacing:
                    self.fill_vrect(x + w, y, spacing, h, background)
                # Position x for next letter
                x += w + spacing

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

    def clear(self):
        self.fill(0)

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

    def lines(self, coords, color):
        """Draw multiple lines.

        Args:
            coords ([[int, int],...]): Line coordinate X, Y pairs
            color (int): RGB565 color value.
        """
        # Starting point
        x1, y1 = coords[0]
        # Iterate through coordinates
        for i in range(1, len(coords)):
            x2, y2 = coords[i]
            self.line(x1, y1, x2, y2, color)
            x1, y1 = x2, y2

    def circle(self, x0, y0, r, color):
        """Draw a circle.
        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB565 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.pixel(x0, y0 + r, color)
        self.pixel(x0, y0 - r, color)
        self.pixel(x0 + r, y0, color)
        self.pixel(x0 - r, y0, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.pixel(x0 + x, y0 + y, color)
            self.pixel(x0 - x, y0 + y, color)
            self.pixel(x0 + x, y0 - y, color)
            self.pixel(x0 - x, y0 - y, color)
            self.pixel(x0 + y, y0 + x, color)
            self.pixel(x0 - y, y0 + x, color)
            self.pixel(x0 + y, y0 - x, color)
            self.pixel(x0 - y, y0 - x, color)

    def ellipse(self, x0, y0, a, b, color):
        """Draw an ellipse.
        Args:
            x0, y0 (int): Coordinates of center point.
            a (int): Semi axis horizontal.
            b (int): Semi axis vertical.
            color (int): RGB565 color value.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.pixel(x0 + x, y0 + y, color)
        self.pixel(x0 - x, y0 + y, color)
        self.pixel(x0 + x, y0 - y, color)
        self.pixel(x0 - x, y0 - y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.pixel(x0 + x, y0 + y, color)
            self.pixel(x0 - x, y0 + y, color)
            self.pixel(x0 + x, y0 - y, color)
            self.pixel(x0 - x, y0 - y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) +
                  a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.pixel(x0 + x, y0 + y, color)
            self.pixel(x0 - x, y0 + y, color)
            self.pixel(x0 + x, y0 - y, color)
            self.pixel(x0 - x, y0 - y, color)


    def rectangle(self, x, y, w, h, color):
        """Draw a rectangle.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB565 color value.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        self.hline(x, y, w, color)
        self.hline(x, y2, w, color)
        self.vline(x, y, h, color)
        self.vline(x2, y, h, color)

    def polygon(self, sides, x0, y0, r, color, rotate=0):
        """Draw an n-sided regular polygon.

        Args:
            sides (int): Number of polygon sides.
            x0, y0 (int): Coordinates of center point.
            r (int): Radius.
            color (int): RGB565 color value.
            rotate (Optional float): Rotation in degrees relative to origin.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        coords = []
        theta = radians(rotate)
        n = sides + 1
        for s in range(n):
            t = 2.0 * pi * s / sides + theta
            coords.append([int(r * cos(t) + x0), int(r * sin(t) + y0)])

        # Cast to python float first to fix rounding errors
        self.lines(coords, color=color)

    def fill_rectangle(self, x, y, w, h, color):
        """Draw a filled rectangle.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB565 color value.
        """
        if self.is_off_grid(x, y, x + w - 1, y + h - 1):
            return
        if w > h:
            self.fill_hrect(x, y, w, h, color)
        else:
            self.fill_vrect(x, y, w, h, color)

    def fill_circle(self, x0, y0, r, color):
        """Draw a filled circle.

        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB565 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.vline(x0, y0 - r, 2 * r + 1, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.vline(x0 + x, y0 - y, 2 * y + 1, color)
            self.vline(x0 - x, y0 - y, 2 * y + 1, color)
            self.vline(x0 - y, y0 - x, 2 * x + 1, color)
            self.vline(x0 + y, y0 - x, 2 * x + 1, color)


    def fill_polygon(self, sides, x0, y0, r, color, rotate=0):
        """Draw a filled n-sided regular polygon.

        Args:
            sides (int): Number of polygon sides.
            x0, y0 (int): Coordinates of center point.
            r (int): Radius.
            color (int): RGB565 color value.
            rotate (Optional float): Rotation in degrees relative to origin.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        # Determine side coordinates
        coords = []
        theta = radians(rotate)
        n = sides + 1
        for s in range(n):
            t = 2.0 * pi * s / sides + theta
            coords.append([int(r * cos(t) + x0), int(r * sin(t) + y0)])
        # Starting point
        x1, y1 = coords[0]
        # Minimum Maximum X dict
        xdict = {y1: [x1, x1]}
        # Iterate through coordinates
        for row in coords[1:]:
            x2, y2 = row
            xprev, yprev = x2, y2
            # Calculate perimeter
            # Check for horizontal side
            if y1 == y2:
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 in xdict:
                    xdict[y1] = [min(x1, xdict[y1][0]), max(x2, xdict[y1][1])]
                else:
                    xdict[y1] = [x1, x2]
                x1, y1 = xprev, yprev
                continue
            # Non horizontal side
            # Changes in x, y
            dx = x2 - x1
            dy = y2 - y1
            # Determine how steep the line is
            is_steep = abs(dy) > abs(dx)
            # Rotate line
            if is_steep:
                x1, y1 = y1, x1
                x2, y2 = y2, x2
            # Swap start and end points if necessary
            if x1 > x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            # Recalculate differentials
            dx = x2 - x1
            dy = y2 - y1
            # Calculate error
            error = dx >> 1
            ystep = 1 if y1 < y2 else -1
            y = y1
            # Calcualte minimum and maximum x values
            for x in range(x1, x2 + 1):
                if is_steep:
                    if x in xdict:
                        xdict[x] = [min(y, xdict[x][0]), max(y, xdict[x][1])]
                    else:
                        xdict[x] = [y, y]
                else:
                    if y in xdict:
                        xdict[y] = [min(x, xdict[y][0]), max(x, xdict[y][1])]
                    else:
                        xdict[y] = [x, x]
                error -= abs(dy)
                if error < 0:
                    y += ystep
                    error += dx
            x1, y1 = xprev, yprev
        # Fill polygon
        for y, x in xdict.items():
            self.hline(x[0], y, x[1] - x[0] + 2, color)

    def fill_vrect(self, x, y, w, h, color):
        """Draw a filled rectangle (optimized for vertical drawing).

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB565 color value.
        """
        if self.is_off_grid(x, y, x + w - 1, y + h - 1):
            return
        chunk_width = 1024 // h
        chunk_count, remainder = divmod(w, chunk_width)
        chunk_size = chunk_width * h
        chunk_x = x
        if chunk_count:
            buf = color.to_bytes(2, 'big') * chunk_size
            for c in range(0, chunk_count):
                self.set_window(chunk_x, y,
                           chunk_x + chunk_width - 1, y + h - 1,
                           buf)
                chunk_x += chunk_width

        if remainder:
            buf = color.to_bytes(2, 'big') * remainder * h
            self.set_window(chunk_x, y,
                       chunk_x + remainder - 1, y + h - 1,
                       buf)

    def fill_hrect(self, x, y, w, h, color):
        """Draw a filled rectangle (optimized for horizontal drawing).

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB565 color value.
        """
        if self.is_off_grid(x, y, x + w - 1, y + h - 1):
            return
        chunk_height = 1024 // w
        chunk_count, remainder = divmod(h, chunk_height)
        chunk_size = chunk_height * w
        chunk_y = y
        if chunk_count:
            buf = color.to_bytes(2, 'big') * chunk_size
            for c in range(0, chunk_count):
                self.set_window(x, chunk_y,
                           x + w - 1, chunk_y + chunk_height - 1,
                           buf)
                chunk_y += chunk_height

        if remainder:
            buf = color.to_bytes(2, 'big') * remainder * w
            self.set_window(x, chunk_y,
                       x + w - 1, chunk_y + remainder - 1,
                       buf)

    def fill_ellipse(self, x0, y0, a, b, color):
        """Draw a filled ellipse.

        Args:
            x0, y0 (int): Coordinates of center point.
            a (int): Semi axis horizontal.
            b (int): Semi axis vertical.
            color (int): RGB565 color value.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.line(x0, y0 - y, x0, y0 + y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.line(x0 - x, y0 - y, x0 - x, y0 + y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) +
                  a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.line(x0 - x, y0 - y, x0 - x, y0 + y, color)


    def text(self, aPos, aString, aColor, aFont, aSize = 1, nowrap = False):

        if aFont == None:
          return

        #Make a size either from single value or 2 elements.
        if (type(aSize) == int) or (type(aSize) == float):
          wh = (aSize, aSize)
        else:
          wh = aSize

        px, py = aPos
        width = wh[0] * aFont["Width"] + 1
        for c in aString:
          self.char((px, py), c, aColor, aFont, wh)
          px += width
          #We check > rather than >= to let the right (blank) edge of the
          # character print off the right of the screen.
          if px + width > self.width:
            if nowrap:
              break
            else:
              py += aFont["Height"] * wh[1] + 1
              px = aPos[0]


    def char(self, aPos, aChar, aColor, aFont, aSizes):

        if aFont == None:
          return

        startchar = aFont['Start']
        endchar = aFont['End']

        ci = ord(aChar)
        if (startchar <= ci <= endchar):
          fontw = aFont['Width']
          fonth = aFont['Height']
          ci = (ci - startchar) * fontw

          charA = aFont["Data"][ci:ci + fontw]
          px = aPos[0]
          if aSizes[0] <= 1 and aSizes[1] <= 1 :
            buf = bytearray(2 * fonth * fontw)
            for q in range(fontw) :
              c = charA[q]
              for r in range(fonth) :
                if c & 0x01 :
                  pos = 2 * (r * fontw + q)
                  buf[pos] = aColor >> 8
                  buf[pos + 1] = aColor & 0xff
                c >>= 1
            self.set_window(aPos[0], aPos[1], aPos[0] + fontw - 1, aPos[1] + fonth - 1, buf)
          else:
            for c in charA :
              py = aPos[1]
              for r in range(fonth) :
                if c & 0x01 :
                  self.fill_rect(px, py, aSizes[0], aSizes[1], aColor)
                py += aSizes[1]
                c >>= 1
              px += aSizes[0]

    def draw_image(self, path, x=0, y=0, w=128, h=128):
        """Draw image from flash.

        Args:
            path (string): Image file path.
            x (int): X coordinate of image left.  Default is 0.
            y (int): Y coordinate of image top.  Default is 0.
            w (int): Width of image.  Default is 128.
            h (int): Height of image.  Default is 128.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        if self.is_off_grid(x, y, x2, y2):
            return
        with open(path, "rb") as f:
            chunk_height = 1024 // w
            chunk_count, remainder = divmod(h, chunk_height)
            chunk_size = chunk_height * w * 2
            chunk_y = y
            if chunk_count:
                for c in range(0, chunk_count):
                    buf = f.read(chunk_size)
                    self.set_window(x, chunk_y,
                               x2, chunk_y + chunk_height - 1,
                               buf)
                    chunk_y += chunk_height
            if remainder:
                buf = f.read(remainder * w * 2)
                self.set_window(x, chunk_y,
                           x2, chunk_y + remainder - 1,
                           buf)

    def draw_sprite(self, buf, x, y, w, h):
        """Draw a sprite (optimized for horizontal drawing).

        Args:
            buf (bytearray): Buffer to draw.
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of drawing.
            h (int): Height of drawing.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        if self.is_off_grid(x, y, x2, y2):
            return
        self.set_window(x, y, x2, y2, buf)

    def load_sprite(self, path, w, h):
        """Load sprite image.

        Args:
            path (string): Image file path.
            w (int): Width of image.
            h (int): Height of image.
        Notes:
            w x h cannot exceed 2048
        """
        buf_size = w * h * 2
        with open(path, "rb") as f:
            return f.read(buf_size)
