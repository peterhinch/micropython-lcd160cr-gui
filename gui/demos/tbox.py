# tbox.py Test/demo of Textbox

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2020 Peter Hinch


import uasyncio as asyncio
from gui.core.lcd160_gui import Screen, IFont
from gui.core.constants import *

from gui.widgets.buttons import Button, RadioButtons
from gui.widgets.label import Label
from gui.widgets.textbox import Textbox

import font10
import font6
font3 = IFont(3)

from lcd_local import setup

# **** STANDARD BUTTON TYPES ****

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')

def fwdbutton(x, y, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)
    Button((x, y), font = font10, callback = fwd, fgcolor = RED,
           text = text, shape = RECTANGLE)

def backbutton():
    def back(button):
        Screen.back()
    Button((109, 107), font = font10, fontcolor = BLACK, callback = back,
           fgcolor = CYAN,  text = 'Back', shape = RECTANGLE)

# **** STANDARDISE CONTROLS ACROSS SCREENS ****
# Appearance for Textbox instances
tbargs = {'fontcolor' : GREEN,
            'fgcolor' : RED,
            'bgcolor' : DARKGREEN,
            'repeat' : False,
            }

# Appearance for buttons
btntable = {'fgcolor' : LIGHTBLUE,
            'font' : font10,
            'width' : 50,
            'litcolor' : GREEN,
            }

# Appearance for labels
labels = {'fontcolor' : WHITE,
            'border' : 2,
            'fgcolor' : RED,
            'bgcolor' : DARKGREEN,
            'font' : font10,
            }

# **** NEXT SCREEN CLASS ****

# Fast populate a textbox
def populate(button, tb):
    s = '''The textbox displays multiple lines of text in a field of fixed dimensions. \
Text may be clipped to the width of the control or may be word-wrapped. If the number \
of lines of text exceeds the height available, scrolling may be performed, either \
by calling a method or by touching the control.
'''
    tb.append(s, ntrim = 100, line = 0)

def clear(button, tb):
    tb.clear()

class FastScreen(Screen):
    def __init__(self, clip):
        super().__init__()
        backbutton()
        tb = Textbox((0, 0), 159, 7, font=font3, clip=clip, tab=64, **tbargs)
        Button((0, 107), text = 'Fill', callback = populate, args = (tb,), **btntable)
        Button((54, 107), text = 'Clear', callback = lambda b, tb: tb.clear(), args = (tb,), **btntable)

# **** TAB SCREEN CLASS ****

def pop_tabs(button, tb):
    s = '''x\t100\t1
alpha\t173\t251
beta\t9184\t876
gamma\t929\t0
abc\tdef\tghi
tabs are text tabs, not decimal tabs.
'''
    tb.append(s)

def clear(button, tb):
    tb.clear()

class TabScreen(Screen):
    def __init__(self, clip):
        super().__init__()
        backbutton()
        tb = Textbox((0, 0), 159, 7, font=font6, clip=clip, tab=50, **tbargs)
        Button((0, 107), text = 'Fill', callback = pop_tabs, args = (tb,), **btntable)
        Button((54, 107), text = 'Clear', callback = lambda b, tb: tb.clear(), args = (tb,), **btntable)

# **** MAIN SCREEEN CLASS ****

# Coroutine slowly populates a text box
async def txt_test(textbox, btns):
    phr0 = ('short', 'longer line', 'much longer line with spaces',
               'antidisestablishmentarianism', 'with\nline break')
    for n in range(len(phr0)):
        textbox.append('Test {:3d} {:s}'.format(n, phr0[n]), 15)
        await asyncio.sleep(1)

    for n in range(n, 15):
        textbox.append('Scroll test {:3d}'.format(n), 15)
        await asyncio.sleep(1)

    if isinstance(btns, tuple):
        for btn in btns:
            btn.greyed_out(False)

# Callback for scroll buttons
def btn_cb(button, tb, n):
    tb.scroll(n)

class SScreen(Screen):
    def __init__(self, clip):
        super().__init__()
        backbutton()
        tb = Textbox((0, 0), 159, 7, font=font3, clip=clip, **tbargs)

        btns = (Button((0, 107), text = 'Up', callback = btn_cb, args = (tb, 1), **btntable),
                Button((54, 107), text = 'Down', callback = btn_cb, args = (tb, -1), **btntable))
        for btn in btns:
            btn.greyed_out(True)  # Disallow until textboxes are populated

        self.reg_task(txt_test(tb, btns))

# **** BASE SCREEN ****

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        table_highlight = [
            {'text' : 'Slow', 'args' : (SScreen, False)},
            {'text' : 'Fast', 'args' : (FastScreen, False)},
            {'text' : 'Tabs', 'args' : (TabScreen, False)},
            {'text' : 'Clip', 'args' : (SScreen, True)},
        ]
        quitbutton()
        def rbcb(button, screen, clip):  # RadioButton callback
            Screen.change(screen, args=(clip,))
        rb = RadioButtons(BLUE, rbcb) # color of selected button
        y = 0
        for t in table_highlight:
            rb.add_button((0, y), font = font10, fgcolor = DARKBLUE,
                          onrelease = False, width = 80, fontcolor = WHITE, **t)
            y += 25

def test():
    print('''Main screen populates text box slowly to show
    wrapping in action. "Fast" screen
    shows fast updates using internal font. "Tab"
    screen shows use of tab characters with Python
    font.
    Text boxes may be scrolled by touching them near
    the top or bottom.''')
    setup()
    Screen.change(BaseScreen)

test()
