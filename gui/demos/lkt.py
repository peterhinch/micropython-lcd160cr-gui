# lkt.py Test/demo of Knob and Dial classes for Pybboard TFT GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# Usage:
# import gui.demos.lkt

from math import pi

from gui.core.constants import *
from gui.core.lcd160_gui import Screen
import font6
import font10
from gui.widgets.knob import Knob
from gui.widgets.dial import Dial
from gui.widgets.label import Label
from gui.widgets.buttons import Button, ButtonList
from lcd_local import setup

# STANDARD BUTTONS

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')


class KnobScreen(Screen):
    def __init__(self):
        super().__init__()
        quitbutton()
        self.dial = Dial((106, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
        k0 = Knob((0, 0), fgcolor = GREEN, bgcolor=DARKBLUE, color = (168, 63, 63),
                  border = 2, cb_end = self.callback, cbe_args = ['Knob1'],
                  cb_move = self.knob_moved, cbm_args = (0,))
        k1 = Knob((53, 0), fgcolor = WHITE, border = 2, arc = pi * 1.5,
                  cb_end = self.callback, cbe_args = ['Knob2'],
                  cb_move = self.knob_moved, cbm_args = (1,))

# On/Off toggle grey style
        self.lbl_style = Label((0, 80), font = font10, value = 'Current style: grey')
        bstyle = ButtonList(self.cb_style)
        bstyle.add_button((0, 107), font = font10, fontcolor = WHITE, fgcolor = RED,
                          text = 'Dim', args = (False,))
        bstyle.add_button((0, 107), font = font10, fontcolor = WHITE, fgcolor = GREEN,
                          text = 'Grey', args = (True,))
# On/Off toggle enable/disable
        bs = ButtonList(self.cb_en_dis)
        self.lst_en_dis = (bstyle, k0, k1)
        bs.add_button((53, 107), font = font10, fontcolor = BLACK, fgcolor = GREEN,
                      text = 'Dis', args = (True,))
        bs.add_button((53, 107), font = font10, fontcolor = BLACK, fgcolor = RED,
                      text = 'En', args = (False,))

# CALLBACKS
# cb_end occurs when user stops touching the control
    def callback(self, knob, control_name):
        print('{} returned {}'.format(control_name, knob.value()))

    def knob_moved(self, knob, pointer):
        val = knob.value() # range 0..1
        self.dial.value(2 * (val - 0.5) * pi, pointer)


    def cb_en_dis(self, button, disable):
        for item in self.lst_en_dis:
            item.greyed_out(disable)

    def cb_style(self, button, desaturate):
        self.lbl_style.value(''.join(('Current style: ', 'grey' if desaturate else 'dim')))
        Screen.set_grey_style(desaturate = desaturate)


def test():
    print('Test TFT panel...')
    setup()
    Screen.change(KnobScreen)

test()
