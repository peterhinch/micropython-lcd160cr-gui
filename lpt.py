# pt.py Test/demo of graph plotting extension for Pybboard TFT GUI

# The MIT License (MIT)
#
# Copyright (c) 2016 Peter Hinch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import uasyncio as asyncio
from lplot import PolarGraph, PolarCurve, CartesianGraph, Curve
from lcd160_gui import Button, Label, Screen
from constants import *
from lcd_local import setup
import font10
from math import sin, pi
from cmath import rect

# STANDARD BUTTONS

def quitbutton():
    def quit(button):
        Screen.shutdown()
    return Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')

def fwdbutton(x, y, screen, text='Next'):
    def fwd(button, screen):
        Screen.change(screen)
    return Button((x, y), font = font10, fontcolor = BLACK, callback = fwd,
                  args = [screen], fgcolor = CYAN, text = text)


def backbutton():
    def back(button):
        Screen.back()
    return Button((139, 0), font = font10, fontcolor = BLACK, callback = back,
           fgcolor = RED,  text = 'X', height = 20, width = 20)

def ovlbutton():
    def fwd(button):
        Screen.change(BackScreen)
    return Button((139, 35), font = font10, fontcolor = BLACK, callback = fwd,
                  fgcolor = CYAN, text = 'O', height = 20, width = 20)

def clearbutton(graph):
    def clear(button):
        graph.clear()
    return Button((139, 71), font = font10, fontcolor = BLACK, callback = clear,
           fgcolor = GREEN,  text = 'C', height = 20, width = 20)

def refreshbutton(curvelist):
    def refresh(button):
        for curve in curvelist:
            curve.show()
    return Button((139, 107), font = font10, fontcolor = BLACK, callback = refresh,
           fgcolor = GREEN,  text = 'R', height = 20, width = 20)

# SCREEN CREATION

class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font10, value = 'Refresh test')
        backbutton()

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font10, value = 'plot module demo')
        Label((0, 22), font = font10, value = 'RT: simulate realtime')
        fwdbutton(0, 51, PolarScreen, 'Polar')
        fwdbutton(0, 79, XYScreen, 'XY')
        fwdbutton(0, 107, RealtimeScreen, 'RT')
        quitbutton()

class PolarScreen(Screen):
    def __init__(self):
        super().__init__()
        backbutton()
        ovlbutton()
        g = PolarGraph((0, 0), border = 4, height=120)
        clearbutton(g)
        curve = PolarCurve(g, self.populate)
        refreshbutton((curve,))

    def populate(self, curve):
        def f(theta):
            return rect(sin(3 * theta), theta) # complex
        nmax = 150
        for n in range(nmax + 1):
            theta = 2 * pi * n / nmax
            curve.point(f(theta))

class XYScreen(Screen):
    def __init__(self):
        super().__init__()
        backbutton()
        ovlbutton()
        g = CartesianGraph((0, 0), height = 127, width = 135, yorigin = 2) # Asymmetric y axis
        clearbutton(g)
        curve1 = Curve(g, self.populate_1, (lambda x : x**3 + x**2 -x,)) # args demo
        curve2 = Curve(g, self.populate_2, color = RED)
        refreshbutton((curve1, curve2))

    def populate_1(self, curve, func):
        x = -1
        while x < 1.01:
            y = func(x)
            curve.point(x, y)
            x += 0.1

    def populate_2(self, curve):
        x = -1
        while x < 1.01:
            y = x**2
            curve.point(x, y)
            x += 0.1

# Simulate slow real time data acquisition and plotting
class RealtimeScreen(Screen):
    def __init__(self):
        super().__init__()
        self.buttonlist = []
        self.buttonlist.append(backbutton())
        self.buttonlist.append(ovlbutton())
        cartesian_graph = CartesianGraph((0, 0), height = 127, width = 127)
        self.buttonlist.append(clearbutton(cartesian_graph))
        curve = Curve(cartesian_graph, self.populate)
        self.buttonlist.append(refreshbutton((curve,)))

    def populate(self, curve):
        loop = asyncio.get_event_loop()
        loop.create_task(self.acquire(curve))

    async def acquire(self, curve):
        for but in self.buttonlist:
            but.greyed_out(True)
        x = -1
        await asyncio.sleep(0)
        while x < 1.01:
            y = max(1 - x * x, 0) # possible precison issue
            curve.point(x, y ** 0.5)
            x += 0.05
            await asyncio.sleep_ms(100)
        x = 1
        while x > -1.01:
            y = max(1 - x * x, 0)
            curve.point(x, -(y ** 0.5))
            x -= 0.05
            await asyncio.sleep_ms(100)
        for but in self.buttonlist:
            but.greyed_out(False)


def pt():
    print('Testing plot module...')
    setup()
    Screen.change(BaseScreen)

pt()
