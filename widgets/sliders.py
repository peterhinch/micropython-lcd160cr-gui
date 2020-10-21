# sliders.py Extension to lcd160gui providing the Slider and HorizSlider classes

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Usage:
# from widgets.sliders import Slider
# or:
# from widgets.sliders import HorizSlider

from core.lcd160_gui import Touchable, get_stringsize, dolittle
from widgets.label import Label
# A slider's text items lie outside its bounding box (area sensitive to touch)

# Buffer sizes: saved region is inclusive of pixels at x + width and y + height hence +1
# Saved data is 2 bytes per pixel.
class Slider(Touchable):
    def __init__(self, location, *, font=None, height=120, width=20, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, slidecolor=None, border=None, 
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[], value=0.0):
        width &= 0xfe # ensure divisible by 2
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, True, None, value)
        self.divisions = divisions
        self.legends = legends if font is not None else None
        self.slidecolor = slidecolor
        super()._set_callbacks(cb_move, cbm_args, cb_end, cbe_args)
        slidewidth = int(width / 1.3) & 0xfe # Ensure divisible by 2
        self.slideheight = 6 # must be divisible by 2
                             # We draw an odd number of pixels:
        self.savebuf = bytearray((self.slideheight + 1) * (slidewidth + 1) * 2)  # 2 bytes per pixel
        b = self.border
        self.pot_dimension = self.height - 2 * (b + self.slideheight // 2)
        width = self.width - 2 * b
        xcentre = self.location[0] + b + width // 2
        self.slide_x0 = xcentre - slidewidth // 2
        self.slide_x1 = xcentre + slidewidth // 2 # slide X coordinates
        self.slide_y = None # Invalidate slide position
        # Prevent Label objects being added to display list when already there.
        self.drawn = False

    def show(self):
        tft = self.tft
        bw = self.border
        width = self.width - 2 * bw
        height = self.pot_dimension # Height of slot
        x = self.location[0] + bw
        y = self.location[1] + bw + self.slideheight // 2 # Allow space above and below slot
        if self._value is None or self.redraw: # Initialising
            self.redraw = False
            self.render_slide(tft, self.bgcolor) # Erase slide if it exists
            dx = width // 2 - 2 
            tft.draw_rectangle(x + dx, y, x + width - dx, y + height, self.fgcolor)
            if self.divisions > 0:
                dy = height / (self.divisions) # Tick marks
                for tick in range(self.divisions + 1):
                    ypos = int(y + dy * tick)
                    tft.draw_hline(x + 1, ypos, dx, self.fgcolor)
                    tft.draw_hline(x + 2 + width // 2, ypos, dx, self.fgcolor) # Add half slot width

            # Legends: if redrawing, they are already on the Screen's display list
            if self.legends is not None and not self.drawn:
                if len(self.legends) <= 1:
                    dy = 0
                else:
                    dy = height / (len(self.legends) -1)
                yl = y + height # Start at bottom
                fhdelta = self.font.height() / 2
                font = self.font
                for legend in self.legends:
                    loc = (x + self.width, int(yl - fhdelta))
                    Label(loc, font = font, fontcolor = tft.text_fgcolor, value = legend)
                    yl -= dy
            self.save_background(tft)
            if self._value is None:
                self.value(self._initial_value, show = False) # Prevent recursion
        self.render_bg(tft)
        self.slide_y = self.update(tft) # Reflect new value in slider position
        self.save_background(tft)
        color = self.slidecolor if self.slidecolor is not None else self.fgcolor
        self.render_slide(tft, color)
        self.drawn = True

    def update(self, tft):
        y = self.location[1] + self.border + self.slideheight // 2
        sliderpos = int(y + self.pot_dimension - self._value * self.pot_dimension)
        return sliderpos - self.slideheight // 2

    def slide_coords(self):
        return self.slide_x0, self.slide_y, self.slide_x1, self.slide_y + self.slideheight

    def save_background(self, tft): # Read background under slide
        if self.slide_y is not None:
            tft.save_region(self.savebuf, *self.slide_coords())

    def render_bg(self, tft):
        if self.slide_y is not None:
            tft.restore_region(self.savebuf, *self.slide_coords())

    def render_slide(self, tft, color):
        if self.slide_y is not None:
            tft.fill_rectangle(*self.slide_coords(), color = color)

    def color(self, color):
        if color != self.fgcolor:
            self.fgcolor = color
            self.redraw = True
            self.show_if_current()

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        self.value((self.location[1] + self.height - y) / self.pot_dimension)

class HorizSlider(Touchable):
    def __init__(self, location, *, font=None, height=20, width=120, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, slidecolor=None, border=None, 
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[], value=0.0):
        height &= 0xfe # ensure divisible by 2
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, True, None, value)
        self.divisions = divisions
        self.legends = legends if font is not None else None
        self.slidecolor = slidecolor
        super()._set_callbacks(cb_move, cbm_args, cb_end, cbe_args)
        slideheight = int(height / 1.3) & 0xfe # Ensure divisible by 2
        self.slidewidth = 6 # must be divisible by 2
                             # We draw an odd number of pixels
        self.savebuf = bytearray((slideheight + 1) * (self.slidewidth + 1) * 2)  # 2 bytes per pixel
        b = self.border
        self.pot_dimension = self.width - 2 * (b + self.slidewidth // 2)
        height = self.height - 2 * b
        ycentre = self.location[1] + b + height // 2
        self.slide_y0 = ycentre - slideheight // 2
        self.slide_y1 = ycentre + slideheight // 2 # slide Y coordinates
        self.slide_x = None # invalidate: slide has not yet been drawn
        # Prevent Label objects being added to display list when already there.
        self.drawn = False

    def show(self):
        tft = self.tft
        bw = self.border
        height = self.height - 2 * bw
        width = self.pot_dimension # Length of slot
        x = self.location[0] + bw + self.slidewidth // 2 # Allow space left and right slot for slider at extremes
        y = self.location[1] + bw
        if self._value is None or self.redraw: # Initialising
            self.redraw = False
            self.render_slide(tft, self.bgcolor) # Erase slide if it exists
            dy = height // 2 - 2 # slot is 4 pixels wide
            tft.draw_rectangle(x, y + dy, x + width, y + height - dy, self.fgcolor)
            if self.divisions > 0:
                dx = width / (self.divisions) # Tick marks
                for tick in range(self.divisions + 1):
                    xpos = int(x + dx * tick)
                    tft.draw_vline(xpos, y + 1, dy, self.fgcolor)
                    tft.draw_vline(xpos, y + 2 + height // 2,  dy, self.fgcolor) # Add half slot width

            # Legends: if redrawing, they are already on the Screen's display list
            if self.legends is not None and not self.drawn:
                if len(self.legends) <= 1:
                    dx = 0
                else:
                    dx = width / (len(self.legends) -1)
                xl = x
                font = self.font
                for legend in self.legends:
                    offset = get_stringsize(legend, self.font)[0] / 2
                    loc = int(xl - offset), y - self.font.height() - bw - 1
                    Label(loc, font = font, fontcolor = tft.text_fgcolor, value = legend)
                    xl += dx
            self.save_background(tft)
            if self._value is None:
                self.value(self._initial_value, show = False) # prevent recursion

        self.render_bg(tft)
        self.slide_x = self.update(tft) # Reflect new value in slider position
        self.save_background(tft)
        color = self.slidecolor if self.slidecolor is not None else self.fgcolor
        self.render_slide(tft, color)
        self.drawn = True

    def update(self, tft):
        x = self.location[0] + self.border + self.slidewidth // 2
        sliderpos = int(x + self._value * self.pot_dimension)
        return sliderpos - self.slidewidth // 2

    def slide_coords(self):
        return self.slide_x, self.slide_y0, self.slide_x + self.slidewidth, self.slide_y1

    def save_background(self, tft): # Read background under slide
        if self.slide_x is not None:
            tft.save_region(self.savebuf, *self.slide_coords())

    def render_bg(self, tft):
        if self.slide_x is not None:
            tft.restore_region(self.savebuf, *self.slide_coords())

    def render_slide(self, tft, color):
        if self.slide_x is not None:
            tft.fill_rectangle(*self.slide_coords(), color = color)

    def color(self, color):
        if color != self.fgcolor:
            self.fgcolor = color
            self.redraw = True
            self.show_if_current()

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        self.value((x - self.location[0]) / self.pot_dimension)
