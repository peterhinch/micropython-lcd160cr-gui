# ldd.py Demo/test program for dropdown list and listbox controls for Pyboard LCD160CR GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# Usage:
# import demos.ldd

from core.constants import *
from core.lcd160_gui import Screen
import font10
from widgets.buttons import Button, ButtonList
from widgets.label import Label
from widgets.listbox import Listbox
from widgets.dropdown import Dropdown
from lcd_local import setup

# STANDARD BUTTONS

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit',)

# **** BASE SCREEN ****

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        quitbutton()
# Dropdown
        self.lbl_dd = Label((0, 80), font = font10, width = 60, border = 2, bgcolor = DARKGREEN, fgcolor = RED)
        self.dropdown = Dropdown((0, 0), font = font10, width = 65, callback = self.cbdb,
                                 elements = ('Dog', 'Cat', 'Rat', 'Goat', 'Pig'))
# Listbox
        self.listbox = Listbox((80, 0), font = font10, width = 79,
                               bgcolor = GREY, fgcolor = YELLOW, select_color = BLUE,
                               elements = ('aardvark', 'zebra', 'armadillo', 'warthog'),
                               callback = self.cblb)

        self.btnrep = Button((0, 40), height = 20, font = font10, callback = self.cbrep, fgcolor = RED,
           text = 'Report', shape = RECTANGLE, width = 60)

# Enable/Disable toggle 
        self.bs_en = ButtonList(self.cb_en_dis)
        self.bs_en.add_button((0, 107), font = font10, fontcolor = BLACK, height = 20, width = 60,
                              fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = (True,))
        self.bs_en.add_button((0, 107), font = font10, fontcolor = BLACK, height = 20, width = 60,
                              fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = (False,))

    def cb_en_dis(self, button, disable):
        self.listbox.greyed_out(disable)
        self.dropdown.greyed_out(disable)
        self.btnrep.greyed_out(disable)

    def cbdb(self, dropdown):
        self.lbl_dd.value(dropdown.textvalue())
        print('dropdown callback:', dropdown.textvalue(), dropdown.value())

    def cblb(self, listbox):
        print('listbox callback:', listbox.textvalue(), listbox.value())

    def cbrep(self, _):
        print('Report:')
        print('listbox', self.listbox.textvalue(), self.listbox.value())
        print('dropdown', self.dropdown.textvalue(), self.dropdown.value())

def test():
    print('Testing TFT...')
    setup()
    Screen.change(BaseScreen)

test()
