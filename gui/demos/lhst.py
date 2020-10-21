# lhst.py Demo/test program for horizontal slider class for Pyboard LCD160CR GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# Usage:
# import gui.demos.lhst

import os
import uasyncio as asyncio
import font6
import font10
from gui.core.constants import *
from gui.core.lcd160_gui import Screen
from gui.widgets.sliders import HorizSlider
from gui.widgets.buttons import Button, ButtonList
from gui.widgets.dial import Dial
from gui.widgets.label import Label
from gui.widgets.meter import Meter
from gui.widgets.led import LED 
from lcd_local import setup

# STANDARD BUTTONS

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')

def to_string(val):
    return '{:3.1f}V'.format(val * 10)

class SliderScreen(Screen):
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
        self.meter = Meter((129, 0), font=font6, legends=('0','5','10'), pointercolor = YELLOW,
                           fgcolor = CYAN)
        self.lbl_result = Label((25, 80), **labels)
        self.led = LED((0, 80), border = 2)
        self.master = HorizSlider((0, 16), font = font6, fgcolor = YELLOW, fontcolor = WHITE,
                                  legends = ('0', '5', '10'), cb_end = self.callback,
                                  cbe_args = ('Master',), cb_move = self.master_moved,
                                  value=0.5, border = 2)
        self.slave = HorizSlider((0, 44), fgcolor = GREEN, cbe_args = ('Slave',),
                                 cb_move = self.slave_moved, border = 2)
        loop = asyncio.get_event_loop()
        loop.create_task(self.coro())
    # On/Off toggle: enable/disable quit button and one slider
        bs = ButtonList(self.cb_en_dis)
        lst_en_dis = [self.slave, self.master]
        button = bs.add_button((0, 107), font = font10, fontcolor = BLACK, fgcolor = GREEN,
                               text = 'Dis', args = [True, lst_en_dis])
        button = bs.add_button((0, 107), font = font10, fontcolor = BLACK, fgcolor = RED,
                               text = 'En', args = [False, lst_en_dis])

# CALLBACKS
# cb_end occurs when user stops touching the control
    def callback(self, slider, device):
        print('{} returned {}'.format(device, slider.value()))

    def master_moved(self, slider):
        val = slider.value()
        self.led.value(val > 0.8)
        self.slave.value(val)
        self.lbl_result.value(to_string(val))

    def cb_en_dis(self, button, disable, itemlist):
        for item in itemlist:
            item.greyed_out(disable)

# Either slave has had its slider moved (by user or by having value altered)
    def slave_moved(self, slider):
        val = slider.value()
        if val > 0.8:
            slider.color(RED)
        else:
            slider.color(GREEN)
        self.lbl_result.value(to_string(val))

# COROUTINE
    async def coro(self):
        oldvalue = 0
        await asyncio.sleep(0)
        while True:
            val = int.from_bytes(os.urandom(1), 1) / 255
            steps = 20
            delta = (val - oldvalue) / steps
            for _ in range(steps):
                oldvalue += delta
                self.meter.value(oldvalue)
                await asyncio.sleep_ms(100)


def test():
    print('Test TFT panel...')
    setup()
    Screen.set_grey_style(desaturate = False) # dim
    Screen.change(SliderScreen)       # Run it!

test()
