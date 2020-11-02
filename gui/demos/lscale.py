# lscale.py Test/demo of scale widget for Pybboard LCD160CR GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Usage:
# import gui.demos.lscale
import uasyncio as asyncio
from gui.core.constants import *
from gui.core.lcd160_gui import Screen
import font10
import font6
from gui.widgets.buttons import Button
from gui.widgets.label import Label
from gui.widgets.scale import Scale
from lcd_local import setup


def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit',)


class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        # Scale with custom variable and legends.
        def legendcb(f):
            return '{:2.0f}'.format(88 + ((f + 1) / 2) * (108 - 88))
        self.scale = Scale((0, 0), font6, width = 159, legendcb = legendcb,
                           fgcolor=GREEN, pointercolor=RED, fontcolor=YELLOW)
        self.reg_task(self.radio())
        # Scale with varying color.
        def tickcb(f, c):
            if f > 0.8:
                return RED
            if f < -0.8:
                return BLUE
            return c
        #Label((0, 50), font = font6, value = 'Random:')
        self.lbl_result = Label((0, 105), font = font10, fontcolor = WHITE, width = 70,
                                border = 2, fgcolor = RED, bgcolor = DARKGREEN)
        self.scale1 = Scale((0, 70), font6, width = 159, tickcb = tickcb,
                           fgcolor=GREEN, pointercolor=RED, fontcolor=YELLOW)
        self.reg_task(self.default())
        quitbutton()

# COROUTINES
    async def radio(self):
        cv = 88.0  # Current value
        val = 108.0  # Target value
        while True:
            v1, v2 = val, cv
            steps = 200
            delta = (val - cv) / steps
            for _ in range(steps):
                cv += delta
                # Map user variable to -1.0..+1.0
                self.scale.value(2 * (cv - 88)/(108 - 88) - 1)
                await asyncio.sleep_ms(200)
            val, cv = v2, v1

    async def default(self):
        cv = -1.0  # Current
        val = 1.0
        while True:
            v1, v2 = val, cv
            steps = 400
            delta = (val - cv) / steps
            for _ in range(steps):
                cv += delta
                self.scale1.value(cv)
                self.lbl_result.value('{:4.3f}'.format(cv))
                await asyncio.sleep_ms(250)
            val, cv = v2, v1


def test():
    setup()
    Screen.change(BaseScreen)

test()
