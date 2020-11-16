# lcd_local_official_esp.py Configuration for Pybboard LCD160CR GUI on ESP32
# running the official firmware

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2020 Peter Hinch

# This file is intended for definition of the local hardware.

# Copy to lcd_local.py on the target.
# This file has been tested on the ESP32 reference board. 

# Arguments for LCD160CR_G are as per official LCD160CR driver with the
# addition of a 'bufsize' kwarg. If provided it should be equal to
# height * max_width * 2 for the largest font in use.
# Default 1058 bytes, allowing fonts upto 23*23 pixels (font14.py)

from gui.core import lcd160cr
from gui.core.lcd160_gui import Screen, LCD160CR_G

from machine import Pin, I2C, SPI

def setup():
    pwr = Pin(33, Pin.OUT)
    # Hardware SPI on native pins for performance
    spi = SPI(1, 10_000_000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    #i2c = I2C(1, scl=Pin(32), sda=Pin(33), freq=1_000_000)  # Works
    # i2c = I2C(0) ENODEV
    #i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=1_000_000)
    #i2c = I2C(1) ENODEV
    i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=1_000_000)
    lcd = LCD160CR_G(pwr=pwr, spi=spi, i2c=i2c)  # Set connection
    lcd.set_orient(lcd160cr.LANDSCAPE)  # and orientation
    Screen.setup(lcd)
