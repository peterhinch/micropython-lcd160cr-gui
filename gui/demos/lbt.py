# lbt.py Test/demo of pushbutton classes for Pybboard TFT GUI

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

# Usage:
# import gui.demos.lbt

from gui.core.constants import *
from gui.core.lcd160_gui import Screen
import font10
from gui.widgets.buttons import Button, ButtonList, RadioButtons
from gui.widgets.label import Label
from gui.widgets.dropdown import Dropdown
from gui.widgets.checkbox import Checkbox
from lcd_local import setup

# STANDARD BUTTONS

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED,
           text = 'Quit')

def backbutton():
    def back(button):
        Screen.back()
    Button((109, 107), font = font10, fontcolor = BLACK, callback = back,
           fgcolor = CYAN,  text = 'Back')

# STANDARD RESULT LABELS

labels = { 'width' : 50,
        'fontcolor' : WHITE,
        'border' : 2,
        'fgcolor' : RED,
        'bgcolor' : DARKGREEN,
        'font' : font10,
        }


# **** CHECKBOX SCREEN ****

class CheckboxScreen(Screen):
    def __init__(self):
        super().__init__()
        self.cb1 = Checkbox((0, 0), callback = self.cbcb, args = (0,))
        self.cb2 = Checkbox((0, 30), fillcolor = RED, callback = self.cbcb, args = (1,))
        self.lstlbl = [Label((30, 0), **labels), Label((30, 30), **labels)]
        self.lbl_result = Label((0, 106), **labels)
        backbutton()
        self.btn_reset = Button((109, 80), font = font10, fgcolor = BLUE,
                               text = 'Reset', fill = True, callback = self.cbreset,
                               onrelease = False, lp_callback = self.callback, lp_args = ('long',))

    def cbreset(self, button):
        self.cb1.value(0)
        self.cb2.value(0)
        self.lbl_result.value('Short')

    def callback(self, button, arg):
        self.lbl_result.value(arg)

    def cbcb(self, checkbox, idx_label):
        if checkbox.value():
            self.lstlbl[idx_label].value('True')
        else:
            self.lstlbl[idx_label].value('False')

# **** RADIO BUTTON SCREEN ****

class RadioScreen(Screen):
    def __init__(self):
        super().__init__()
        table = [
            {'text' : '1', 'args' : ('one',)},
            {'text' : '2', 'args' : ('two',)},
            {'text' : '3', 'args' : ('three',)},
            {'text' : '4', 'args' : ('four',)},
        ]
        Label((0, 0), font = font10, value = 'Radio Buttons')
        x = 0
        self.rb = RadioButtons(BLUE, self.callback) # color of selected button
        self.rb0 = None
        for t in table:
            button = self.rb.add_button((x, 30), shape = CIRCLE, font = font10, fontcolor = WHITE,
                                fgcolor = (0, 0, 90), height = 30, width = 30, **t)
            if self.rb0 is None: # Save for reset button callback
                self.rb0 = button
            x += 43
        self.lbl_result = Label((0, 106), **labels)
        backbutton()
        self.btn_reset = Button((109, 80), font = font10, fgcolor = BLUE, text = 'Reset',
                                fill = True, callback = self.cbreset, onrelease = False,
                                lp_callback = self.callback, lp_args = ('long',))

    def callback(self, button, arg):
        self.lbl_result.value(arg)

    def cbreset(self, button):
        self.rb.value(self.rb0)
        self.lbl_result.value('Short')

# **** HIGHLIGHT SCREEN ****

class HighlightScreen(Screen):
    def __init__(self):
        super().__init__()
# tabulate data that varies between buttons
        table = [
            {'text' : 'F', 'args' : ('fwd',)},
            {'text' : 'B', 'args' : ('back',)},
            {'text' : 'U', 'args' : ('up',)},
            {'text' : 'D', 'args' : ('down',)},
        ]
        Label((0, 0), font = font10, value = 'Highlight Buttons')
# Highlighting buttons
        x = 0
        for t in table:
            Button((x, 30), shape = CIRCLE, fgcolor = GREY, fontcolor = BLACK, litcolor = WHITE,
                font = font10, callback = self.callback, height = 30, **t)
            x += 43
        self.lbl_result = Label((0, 106), **labels)
        backbutton()

    def callback(self, button, arg):
        self.lbl_result.value(arg)

# **** ASSORTED SCREEN ****

class AssortedScreen(Screen):
    def __init__(self):
        super().__init__()
# These tables contain args that differ between members of a set of related buttons
        table = [
            {'fgcolor' : GREEN, 'text' : 'Y', 'args' : ('Oui',),
                'fontcolor' : (0, 0, 0), 'height' : 30, 'shape' : CIRCLE},
            {'fgcolor' : RED, 'text' : 'N', 'args' : ('Non',),
                'height' : 30, 'shape' : CIRCLE},
            {'fgcolor' : BLUE, 'bgcolor' : BLACK, 'text' : '?',
                'args' : ('Que?',), 'fill': False, 'height' : 30, 'shape' : CIRCLE},
            {'fgcolor' : GREY, 'text' : '$', 'args' : ('Rats',),
                'height' : 30, 'width' : 30, 'shape' : CLIPPED_RECT},
        ]
# A Buttonset with two entries
        table_buttonset = [
            {'fgcolor' : YELLOW, 'text' : 'Start', 'args' : ('Live',)},
            {'fgcolor' : RED, 'text' : 'Stop', 'args' : ('Die',)},
        ]


# Uncomment this line to see 'skeleton' style greying-out:
#        Screen.tft.grey_color()
        self.lbl_result = Label((109, 53), **labels)
        backbutton()

# Button assortment
        self.buttons = []
        x = 0
        for t in table:
            b = Button((x, 0), font = font10, callback = self.callback, **t)
            self.buttons.append(b)
            x += 43


# Start/Stop toggle
        self.bs = ButtonList(self.callback)
        self.buttons.append(self.bs)
        self.bs0 = None
        for t in table_buttonset: # Buttons overlay each other at same location
            button = self.bs.add_button((0, 53), shape = CLIPPED_RECT, font = font10,
                                        width = 60, fontcolor = BLACK, **t)
            if self.bs0 is None: # Save for reset button callback
                self.bs0 = button



# Reset button
        r = self.btn_reset = Button((109, 80), font = font10,
                                fgcolor = BLUE, text = 'Reset', fill = True,
                                callback = self.cbreset, onrelease = False,
                                lp_callback = self.callback, lp_args = ('long',))
        self.buttons.append(r)

# Enable/Disable toggle 
        self.bs_en = ButtonList(self.cb_en_dis)
        self.bs_en.add_button((0, 107), font = font10, fontcolor = BLACK, width = 60,
                              fgcolor = GREEN, text = 'Disable', args = (True,))
        self.bs_en.add_button((0, 107), font = font10, fontcolor = BLACK, width = 60,
                              fgcolor = RED, text = 'Enable', args = (False,))

    def callback(self, button, arg):
        self.lbl_result.value(arg)

    def cbreset(self, button):
        self.bs.value(self.bs0)
        self.lbl_result.value('Short')

    def cb_en_dis(self, button, disable):
        for item in self.buttons:
            item.greyed_out(disable)

# **** BASE SCREEN ****

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        table_highlight = [
            {'text' : '1', 'args' : (HighlightScreen,)},
            {'text' : '2', 'args' : (RadioScreen,)},
            {'text' : '3', 'args' : (AssortedScreen,)},
            {'text' : '4', 'args' : (CheckboxScreen,)},
        ]
        quitbutton()
        Label((0, 0), font = font10, value = 'Choose screen')
        self.lst_en_dis = []
        x = 0
        for t in table_highlight:
            b = Button((x, 25), font = font10, shape = CIRCLE, fgcolor = BLUE,
                       fontcolor = BLACK, callback = self.callback,
                       height = 30, **t)
            self.lst_en_dis.append(b)
            x += 43
# Enable/Disable toggle 
        self.bs_en = ButtonList(self.cb_en_dis)
        self.bs_en.add_button((0, 107), font = font10, fontcolor = BLACK, width = 60,
                              fgcolor = GREEN, text = 'Disable', args = (True,))
        self.bs_en.add_button((0, 107), font = font10, fontcolor = BLACK, width = 60,
                              fgcolor = RED, text = 'Enable', args = (False,))


    def callback(self, button, screen):
        Screen.change(screen)

    def cb_en_dis(self, button, disable):
        for item in self.lst_en_dis:
            item.greyed_out(disable)


def test():
    print('Testing TFT...')
    setup()
    Screen.change(BaseScreen)

test()
