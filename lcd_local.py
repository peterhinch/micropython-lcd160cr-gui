# lcd_local.py Configuration for Pybboard LCD160CR GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# This file is intended for definition of the local hardware.


# Arguments for LCD160CR_G are as per official LCD160CR driver with the
# addition of a 'bufsize' kwarg. If provided it should be equal to
# height * max_width * 2 for the largest font in use.
# Default 1058 bytes, allowing fonts upto 23*23 pixels (font14.py)

from gui.core import lcd160cr
from gui.core.lcd160_gui import Screen, LCD160CR_G

def setup():
    lcd = LCD160CR_G("Y")  # Set connection
    lcd.set_orient(lcd160cr.LANDSCAPE)  # and orientation
    Screen.setup(lcd)
