# checkbox.py Extension to lcd160gui providing the Checkbox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Usage:
# from widgets.checkbox import Checkbox

from core.lcd160_gui import Touchable, dolittle

class Checkbox(Touchable):
    def __init__(self, location, *, height=20, fillcolor=None,
                 fgcolor=None, bgcolor=None, callback=dolittle, args=[], value=False, border=None):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border, False, value, None)
        super()._set_callbacks(callback, args)
        self.fillcolor = fillcolor

    def show(self):
        if self._initial_value is None:
            self._initial_value = True
            value = self._value # As passed to ctor
            if value is None:
                self._value = False # special case: don't execute callback on initialisation
            else:
                self._value = not value # force redraw
                self.value(value)
                return
        self._show()

    def _show(self):
        tft = self.tft
        bw = self.border
        x = self.location[0] + bw
        y = self.location[1] + bw
        height = self.height - 2 * bw
        x1 = x + height
        y1 = y + height
        if self._value:
            if self.fillcolor is not None:
                tft.fill_rectangle(x, y, x1, y1, self.fillcolor)
        else:
            tft.fill_rectangle(x, y, x1, y1, self.bgcolor)
        tft.draw_rectangle(x, y, x1, y1, self.fgcolor)
        if self.fillcolor is None and self._value:
            tft.draw_line(x, y, x1, y1, self.fgcolor)
            tft.draw_line(x, y1, x1, y, self.fgcolor)

    def _touched(self, x, y): # Was touched
        self.value(not self._value) # Upddate and refresh

