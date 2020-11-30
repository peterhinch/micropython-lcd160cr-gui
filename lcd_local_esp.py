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
from time import sleep_ms
def setup():
    pwr = Pin(25, Pin.OUT)
    pwr(1)
    sleep_ms(100)
    # Hardware SPI on native pins for performance. See examples in doc
    # http://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus
    # Seems to be necessary to explicitly state pin ID's even when using defaults
    spi = SPI(1, 10_000_000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    i2c = I2C(0, freq=1_000_000)  # As per examples in docs, don't need to specify defaults
    # Alternatives. Note pin 19 conflicts with native I2C(0)
    #spi = SPI(2, 10_000_000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
    #i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=1_000_000)
    #i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=1_000_000)

    lcd = LCD160CR_G(pwr=pwr, spi=spi, i2c=i2c)  # Set connection
    lcd.set_orient(lcd160cr.LANDSCAPE)  # and orientation
    Screen.setup(lcd)
