# sliders.py Extension to lcd160gui providing the Listbox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Usage:
# from widgets.listbox import Listbox

from gui.core.lcd160_gui import Touchable, print_left, dolittle
from gui.core.constants import *

class Listbox(Touchable):
    def __init__(self, location, *, font, elements, width=80, value=0, border=2,
                 fgcolor=None, bgcolor=None, fontcolor=None, select_color=LIGHTBLUE,
                 callback=dolittle, args=[]):
        self.entry_height = font.height() + 2 # Allow a pixel above and below text
        bw = border if border is not None else 0 # Replicate Touchable ctor's handling of self.border
        height = self.entry_height * len(elements) + 2 * bw
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, False, value, None)
        super()._set_callbacks(callback, args)
        self.select_color = select_color
        tft = self.tft
        self.select_style = tft.text_style((self.fgcolor, select_color, self.font))
        fail = False
        try:
            self.elements = [s for s in elements if type(s) is str]
        except:
            fail = True
        else:
            fail = len(self.elements) == 0
        if fail:
            raise ValueError('elements must be a list or tuple of one or more strings')
        if value >= len(self.elements):
            value = 0
        self._value = value  # No callback until user touches

    def show(self):
        tft = self.tft
        bw = self.border
        length = len(self.elements)
        x = self.location[0]
        y = self.location[1]
        xs = x + bw # start and end of text field
        xe = x + self.width - 2 * bw
        tft.fill_rectangle(xs, y + 1, xe, y - 1 + self.height - 2 * bw, self.bgcolor)
        for n in range(length):
            ye = y + n * self.entry_height
            if n == self._value:
                tft.fill_rectangle(xs, ye + 1, xe, ye + self.entry_height - 1, self.select_color)
                print_left(tft, xs, ye + 1, self.elements[n], self.select_style)
            else:
                print_left(tft, xs, ye + 1, self.elements[n], self.text_style)

    def textvalue(self, text=None): # if no arg return current text
        if text is None:
            return self.elements[self._value]
        else: # set value by text
            try:
                v = self.elements.index(text)
            except ValueError:
                v = None
            else:
                if v != self._value:
                    self.value(v)
            return v

    def _touched(self, x, y):
        dy = y - (self.location[1])
        self._initial_value = min(dy // self.entry_height, len(self.elements) -1)

    def _untouched(self):
        if self._initial_value is not None:
            self._value = -1  # Force update on every touch
            self.value(self._initial_value, show = True)
            self._initial_value = None
