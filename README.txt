MicroPython driver for ST7789v LCD as found on the board "TTGO T-Display ESP32 CP2104 WiFi bluetooth Module 1.14 Inch LCD Development Board LILYGO for Arduino"

I have not found any library that will work with this Chinese clone DevBoard plug-n-play, so I had to do some coding.

The driver is a draft and mix of code from following repositories: 
  https://github.com/devbis/st7789py_mpy
  https://github.com/lewisxhe/mPython_ST7789
  
The driver doesn't draw text or pictures, only few primitives:
    - rectangle
    - filled rectange
    - line
    - horizontal line
    - vertical line
    - pixel

