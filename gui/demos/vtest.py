# vtest.py Test/demo of VectorDial

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2020 Peter Hinch

# Updated for uasyncio V3

import os
import time
from cmath import rect, pi
import uasyncio as asyncio

from gui.core.lcd160_gui import Screen
from gui.core.constants import *

from gui.widgets.buttons import Button, RadioButtons
from gui.widgets.label import Label
from gui.widgets.vectors import Pointer, VectorDial

import font6
import font10
from lcd_local import setup

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')

def fwdbutton(cls_screen):
    def fwd(button):
        Screen.change(cls_screen)
    Button((0, 107), font = font10, callback = fwd, fgcolor = RED,
           onrelease=False, text = 'Next', shape = RECTANGLE)

def backbutton():
    def back(button):
        Screen.back()
    Button((109, 107), font = font10, fontcolor = BLACK, callback = back,
           fgcolor = CYAN, text = 'Back', shape = RECTANGLE)

class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font6, value = 'Ensure back')
        Label((0, 20), font = font6, value = 'refreshes properly')
        backbutton()

# Create a random vector. Interpolate between current vector and the new one.
# Change pointer color dependent on magnitude.
async def ptr_test(dial):
    ptr = Pointer(dial)
    v = 0j
    steps = 20  # No. of interpolation steps
    grv = lambda: (int.from_bytes(os.urandom(1), 1) -128) / 128  # Random: range -1.0 to +1.0
    while True:
        v1 = grv() + 1j * grv()  # Random vector
        dv = (v1 - v) / steps  # Interpolation vector
        for _ in range(steps):
            v += dv
            mag = abs(v)
            if mag < 0.3:
                ptr.value(v, BLUE)
            elif mag < 0.7:
                ptr.value(v, GREEN)
            else:
                ptr.value(v, RED)
            await asyncio.sleep_ms(200)

# Analog clock demo. Note this could also be achieved using the Dial class.
async def aclock(dial, lblday, lblmon, lblyr, lbltim):
    uv = lambda phi : rect(1, phi)  # Return a unit vector of phase phi
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
              'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths. Position at top.
    mstart = 0 + 1j
    sstart = 0 + 1j 

    while True:
        t = time.localtime()
        hrs.value(hstart * uv(-t[3] * pi/6 - t[4] * pi / 360), CYAN)
        mins.value(mstart * uv(-t[4] * pi/30), CYAN)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        lblday.value('{}'.format(days[t[6]]))
        lblmon.value('{} {}'.format(t[2], months[t[1] - 1]))
        lblyr.value('{}'.format(t[0]))
        await asyncio.sleep(1)

class VecScreen(Screen):
    def __init__(self):
        super().__init__()
        fwdbutton(BackScreen)
        backbutton()
        # Set up random vector display with two pointers
        dial = VectorDial((0, 0), ticks = 12, fgcolor = YELLOW, arrow = True)
        self.reg_task(ptr_test(dial))
        self.reg_task(ptr_test(dial))

class ClockScreen(Screen):
    def __init__(self):
        super().__init__()
        labels = {'fontcolor' : WHITE,
                  'border' : 2,
                  'fgcolor' : RED,
                  'bgcolor' : DARKGREEN,
                  'font' : font6,
                  }
        fwdbutton(BackScreen)
        backbutton()
        # Set up clock display: instantiate labels
        lblday = Label((80, 0), width = 79, **labels)
        lblmon = Label((99, 23), width = 60, **labels)
        lblyr = Label((99, 46), width = 60, **labels)
        lbltim = Label((99, 69), width = 60, **labels)
        dial = VectorDial((0, 0), height = 80, ticks = 12, fgcolor = GREEN, pip = GREEN)
        self.reg_task(aclock(dial, lblday, lblmon, lblyr, lbltim))

class StartScreen(Screen):
     def __init__(self):
        super().__init__()
        table = [
            {'text' : 'Clock', 'args' : (ClockScreen,)},
            {'text' : 'Compass', 'args' : (VecScreen,)},
        ]
        quitbutton()
        Label((0, 0), font = font10, value = 'Display format')
        def rbcb(button, screen):  # RadioButton callback
            Screen.change(screen)
        rb = RadioButtons(BLUE, rbcb) # color of selected button
        y = 25
        for t in table:
            rb.add_button((0, y), font = font10, fgcolor = DARKBLUE,
                          width = 100, fontcolor = WHITE, **t)
            y += 40
   
def test():
    print('Test TFT panel...')
    setup()
    Screen.change(StartScreen)

test()
