# lcd_local_official_esp.py Configuration for Pybboard LCD160CR GUI on ESP32
# running the official firmware

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2020 Peter Hinch


# Copy to lcd_local.py on the target

# This file is intended for definition of the local hardware.

# Arguments for LCD160CR_G are as per official LCD160CR driver with the
# addition of a 'bufsize' kwarg. If provided it should be equal to
# height * max_width * 2 for the largest font in use.
# Default 1058 bytes, allowing fonts upto 23*23 pixels (font14.py)

import lcd160cr
from lcd160_gui import Screen, LCD160CR_G
from machine import Pin, I2C, SPI

def setup():
    pwr = Pin(25, Pin.OUT)
    spi = SPI(2, baudrate=8000000, sck=Pin(18), mosi=Pin(23))
    i2c = i2c = I2C(-1, scl=Pin(32), sda=Pin(33))
    lcd = LCD160CR_G(pwr=pwr, spi=spi, i2c=i2c)  # Set connection
    lcd.set_orient(lcd160cr.LANDSCAPE)  # and orientation
    Screen.setup(lcd)
