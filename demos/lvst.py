# vst.py Demo/test program for vertical slider class for Pyboard TFT GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# Usage:
# import demos.vst

import uasyncio as asyncio
from math import pi
import font6
import font10
from core.constants import *
from core.lcd160_gui import Screen
from widgets.sliders import Slider
from widgets.buttons import Button, ButtonList
from widgets.dial import Dial
from widgets.label import Label
from lcd_local import setup


# STANDARD BUTTON

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')

def to_string(val):
    return '{:3.1f}V'.format(val * 10)

class VerticalSliderScreen(Screen):
    def __init__(self):
        super().__init__()
        labels = { 'width' : 50,
                'fontcolor' : WHITE,
                'border' : 2,
                'fgcolor' : RED,
                'bgcolor' : DARKGREEN,
                'font' : font10,
                }
        quitbutton()
        self.dial = Dial((109, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
        self.lbl_result = Label((109, 80), **labels)
        self.master = Slider((0, 5), font = font6, fgcolor = YELLOW, fontcolor = WHITE,
                             legends = ('0', '5', '10'), cb_end = self.callback,
                             cbe_args = ('Master',), cb_move = self.master_moved,
                             value=0.5, border = 2)
        self.slave = Slider((60, 5), fgcolor = GREEN, cbe_args = ('Slave',),
                            cb_move = self.slave_moved, border = 2)
        loop = asyncio.get_event_loop()
        loop.create_task(self.coro())
    # On/Off toggle: enable/disable quit button and one slider
        bs = ButtonList(self.cb_en_dis)
        lst_en_dis = [self.slave, self.master]
        button = bs.add_button((109, 53), font = font10, fontcolor = BLACK, fgcolor = GREEN,
                               text = 'Dis', args = [True, lst_en_dis])
        button = bs.add_button((109, 53), font = font10, fontcolor = BLACK, fgcolor = RED,
                               text = 'En', args = [False, lst_en_dis])

# CALLBACKS
# cb_end occurs when user stops touching the control
    def callback(self, slider, device):
        print('{} returned {}'.format(device, slider.value()))

    def master_moved(self, slider):
        val = slider.value()
        self.slave.value(val)
        self.lbl_result.value(to_string(val))

    def cb_en_dis(self, button, disable, itemlist):
        for item in itemlist:
            item.greyed_out(disable)

# Slave has had its slider moved (by user or by having value altered)
    def slave_moved(self, slider):
        val = slider.value()
        if val > 0.8:
            slider.color(RED)
        else:
            slider.color(GREEN)
        self.lbl_result.value(to_string(val))

# COROUTINE
    async def coro(self):
        angle = 0
        while True:
            await asyncio.sleep_ms(100)
            delta = self.slave.value()
            angle += pi * 2 * delta / 10
            self.dial.value(angle)
            self.dial.value(angle /10, 1)


def test():
    print('Test TFT panel...')
    setup()
    Screen.set_grey_style(desaturate = False) # dim
    Screen.change(VerticalSliderScreen)       # Run it!

test()
