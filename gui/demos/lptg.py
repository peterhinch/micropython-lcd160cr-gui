# lptg.py Test/demo of graph plotting extension for Pybboard TFT GUI
# Tests time sequence and generators as populate functions.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# Usage:
# import gui.demos.lptg

import uasyncio as asyncio
from math import sin, cos, pi
from cmath import rect

from gui.core.lplot import PolarGraph, PolarCurve, CartesianGraph, Curve, TSequence
from gui.core.lcd160_gui import Screen
from gui.core.constants import *

import font10
from gui.widgets.buttons import Button
from gui.widgets.label import Label 
from lcd_local import setup

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


def backbutton(cb=lambda *_: None):
    def back(button):
        cb()
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
        Label((0, 0), font = font10, value = 'plot module: gens')
        fwdbutton(0, 23, Tseq, 'TSeq')
        fwdbutton(0, 51, PolarScreen, 'Polar')
        fwdbutton(0, 79, XYScreen, 'XY')
        fwdbutton(0, 107, RealtimeScreen, 'RT')
        fwdbutton(60, 51, PolarORScreen, 'Over')
        fwdbutton(60, 79, DiscontScreen, 'Lines')
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

    def populate(self, curve):  # Test generator function as bound method
        def f(theta):
            return rect(sin(3 * theta), theta) # complex
        nmax = 150
        for n in range(nmax + 1):
            theta = 2 * pi * n / nmax
            yield f(theta)


# Test clipping
class PolarORScreen(Screen):
    def __init__(self):
        super().__init__()
        def populate(curve, rot):
            def f(theta):
                return rect(1.15*sin(5 * theta), theta)*rot # complex
            nmax = 150
            for n in range(nmax + 1):
                theta = 2 * pi * n / nmax
                yield f(theta)

        backbutton()
        ovlbutton()
        g = PolarGraph((5, 5), border = 4, height=110)
        clearbutton(g)
        curve = PolarCurve(g, populate, (1,))
        curve1 = PolarCurve(g, populate, (rect(1, pi/5),), color=RED)
        refreshbutton((curve, curve1))


class XYScreen(Screen):
    def __init__(self):
        super().__init__()
        def populate_1(curve, func):
            x = -1
            while x < 1.01:
                y = func(x)
                yield x, y
                x += 0.1

        def populate_2(curve):
            x = -1
            while x < 1.01:
                y = x**2
                yield x, y
                x += 0.1

        backbutton()
        ovlbutton()
        g = CartesianGraph((0, 0), height = 127, width = 135, yorigin = 2) # Asymmetric y axis
        clearbutton(g)
        curve1 = Curve(g, populate_1, (lambda x : x**3 + x**2 -x,)) # args demo
        curve2 = Curve(g, populate_2, color = RED)
        refreshbutton((curve1, curve2))


# Test of discontinuous curves and those which provoke clipping
class DiscontScreen(Screen):
    def __init__(self):
        super().__init__()
        def populate_3(curve):
            for x, y in ((-2, -0.2), (-2, 0.2), (-0.2, -2), (0.2, -2), (2, 0.2), (2, -0.2), (0.2, 2), (-0.2, 2)):
                yield x, y
                yield 0, 0
                yield None, None

        def populate_1(curve, mag):
            theta = 0
            delta = pi/32
            while theta <= 2 * pi:
                yield mag*sin(theta), mag*cos(theta)
                theta += delta

        backbutton()
        ovlbutton()
        g = CartesianGraph((5, 5), height = 115, width = 115)
        clearbutton(g)
        curve1 = Curve(g, populate_1, (1.1,))
        curve2 = Curve(g, populate_1, (1.05,), color=RED)
        curve3 = Curve(g, populate_3, color=BLUE)
        refreshbutton((curve1, curve2, curve3))


# Simulate slow real time data acquisition and plotting
class RealtimeScreen(Screen):
    def __init__(self):
        super().__init__()
        self.buttonlist = []
        self.buttonlist.append(backbutton())
        self.buttonlist.append(ovlbutton())
        cartesian_graph = CartesianGraph((0, 0), height = 127, width = 127)
        self.buttonlist.append(clearbutton(cartesian_graph))
        curve = Curve(cartesian_graph, self.go)
        self.buttonlist.append(refreshbutton((curve,)))

    def go(self, curve):
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

class Tseq(Screen):
    def __init__(self):
        global acq_task
        super().__init__()
        def cancel():
            acq_task.cancel()
        backbutton(cancel)
        g = CartesianGraph((0, 0), height = 127, width = 127, xorigin = 10)
        tsy = TSequence(g, YELLOW, 50)
        tsr = TSequence(g, RED, 50)
        acq_task = asyncio.create_task(self.acquire(g, tsy, tsr))

    async def acquire(self, graph, tsy, tsr):
        t = 0.0
        while True:
            graph.clear()
            tsy.add(0.9 * sin(t))
            tsr.add(0.4 * cos(t))
            await asyncio.sleep_ms(500)
            t += 0.1

def pt():
    print('Testing plot module...')
    setup()
    Screen.change(BaseScreen)

pt()
