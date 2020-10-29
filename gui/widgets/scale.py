# scale.py Extension to lcd160gui providing the Scale class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Usage:
# from widgets.scale import Scale

from gui.core.lcd160_gui import NoTouch, print_left, get_stringsize
from gui.core.constants import * 

_FMIN = -1.0  # Default range -1.0..+1.0
_FMAX = 1.0

class Scale(NoTouch):
    def __init__(self, location, font, *,
                 divs=2000, legendcb=None,
                 height=0, width=100, border=2, fgcolor=None, bgcolor=None,
                 pointercolor=None, fontcolor=None, value=0.0):
        if divs % 20:
            raise ValueError('divs arg must be divisible by 20')
        self.divs = divs
        def lcb(f):
            return '{:3.1f}'.format(f)
        self.legendcb = legendcb if legendcb is not None else lcb 
        bgcolor = self.tft.get_bgcolor() if bgcolor is None else bgcolor
        text_ht = font.height()
        ctrl_ht = 12  # Minimum height for ticks
        min_ht = text_ht + 2 * border + 2  # Ht of text, borders and gap between text and ticks
        if height < min_ht + ctrl_ht:
            height = min_ht + ctrl_ht
        else:
            ctrl_ht = height - min_ht
        width &= 0xfffe  # Make divisible by 2: avoid 1 pixel pointer offset
        NoTouch.__init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, value, None)
        border = self.border # border width
        self.x0 = self.location[0] + border
        self.x1 = self.location[0] + self.width - border
        self.y0 = self.location[1] + border
        self.y1 = self.location[1] + self.height - border
        self.pointercolor = pointercolor if pointercolor is not None else self.fgcolor
        # Geometry of scale graphic. Length is split into 20 divisions.
        self.dx : float = (self.x1 - self.x0) / 20  # x change per 10 units of value
        # Define tick dimensions
        ytop = self.y0 + text_ht + 2  # Top of scale graphic (2 pixel gap)
        ycl = ytop + (self.y1 - ytop) // 2  # Centre line
        self.sdl = round(ctrl_ht * 1 / 3)  # Length of small tick.
        self.sdy0 = ycl - self.sdl // 2
        self.mdl = round(ctrl_ht * 2 / 3)  # Medium tick
        self.mdy0 = ycl - self.mdl // 2
        self.ldl = ctrl_ht  # Large tick
        self.ldy0 = ycl - self.ldl // 2

    def show(self):
        tft = self.tft
        x0: int = self.x0  # Internal rectangle occupied by scale and text
        x1: int = self.x1
        y0: int = self.y0
        y1: int = self.y1
        tft.fill_rectangle(x0, y0, x1, y1, self.bgcolor)
        # Scale is drawn using ints where possible. Each division is 10 units.
        dx: float = self.dx  # x change per 10 units of value
        val: int = round(self.divs * (self._value - _FMIN) / (_FMAX - _FMIN))  # 0..divs
        iv: int  # val // 10: val at a tick position
        d: int  # val % 10: offset relative to a tick position
        fx: float  # Current x position: must be a float for precision
        if val >= 100:  # Whole LHS of scale will be drawn
            iv, d = divmod(val - 100, 10)  # Initial value
            fx = x0 + dx - (dx * d) / 10  # Location of 1st tick: ensure within border
            iv += 1
        else:  # Scale will scroll right
            iv = 0
            fx = x0 + (dx * (100 - val)) / 10

        imax: int = self.divs // 10
        while True:
            x: int = round(fx)  # Current X position
            ys: int  # Start Y position for tick
            yl: int  # tick length
            if x > x1 or iv > imax:  # Out of space or data (scroll left)
                break
            if not iv % 10:
                txt = self.legendcb((_FMAX - _FMIN) * iv / imax + _FMIN)
                tlen, _ = get_stringsize(txt, self.font)
                print_left(tft, min(x, x1 - tlen), y0, txt, self.text_style)
                ys = self.ldy0  # Large tick
                yl = self.ldl
            elif not iv % 5:
                ys = self.mdy0
                yl = self.mdl
            else:
                ys = self.sdy0
                yl = self.sdl
            tft.draw_vline(x, ys, yl, self.fgcolor)  # Draw tick
            fx += dx
            iv += 1

        tft.draw_vline(x0 + (x1 - x0) // 2, y0, y1 - y0, self.pointercolor) # Draw pointer

    def value(self, val=None): # User method to get or set value
        if val is not None:
            val = min(max(val, _FMIN), _FMAX)
            if val != self._value:
                self._value = val
                self._value_change(True)
        return self._value
