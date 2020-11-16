# lcd160_gui.py Micropython GUI library for LCD160CR displays

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import framebuf
from uctypes import bytearray_at, addressof
fast_mode = False
try:
    from gui.framebuf_utils.framebuf_utils import render
    fast_mode = True
    print('Using fast mode')
except ValueError:
    print('Ignoring framebuf_utils.mpy: compiled for incorrect architecture.')
except ImportError:
    pass

import uasyncio as asyncio
import gc
from gui.core.lcd160cr import LCD160CR
from gui.primitives.delay_ms import Delay_ms
from gui.core.constants import *
gc.collect()

# *********** UTILITY FUNCTIONS ***********

class _A():
    pass

ClassType = type(_A)

class UguiException(Exception):
    pass

# Null function
dolittle = lambda *_ : None

async def _g():
    pass
type_coro = type(_g())

# *********** INTERNAL FONTS ***********

class IFont:
    size = ((4, 5), (6, 7), (8, 8), (9, 13))  # (w, h) for each font
    def __init__(self, family, scale=0, bold_h=0, bold_v=0):
        self.bold = (bold_h & 3) | ((bold_v & 3) << 2)
        self.scale = scale
        self.width = (scale + 1) * self.size[family][0]
        self.vheight = (scale + 1) * self.size[family][1]
        self.family = family

    def stringsize(self, s):
        return len(s) * self.width, self.vheight

    def render(self, tft, x, y, s, style):
        tft.set_pos(x, y)
        tft.set_text_color(tft.rgb(*style[0]), tft.rgb(*style[1]))
        tft.set_font(self.family, self.scale, self.bold, 0, 0)
        tft.write(s)

    def height(self):
        return self.vheight

    def max_width(self):
        return self.width

    def hmap(self):
        return True

    def reverse(self):
        return False

    def monospaced(self):
        return True

# *********** STRINGS ***********

def get_stringsize(s, font):
    if isinstance(font, IFont):
        return font.stringsize(s)
    hor = 0
    for c in s:
        _, vert, cols = font.get_ch(c)
        hor += cols
    return hor, vert


# Style is (fgcolor, bgcolor, font)
def print_centered(tft, x, y, s, style):
    font = style[2]
    length, height = get_stringsize(s, font)
    x, y = max(x - length // 2, 0), max(y - height // 2, 0)
    if isinstance(font, IFont):
        return font.render(tft, x, y, s, style)
    tft.text_style(style)
    tft.set_text_pos(x, y)
    tft.print_string(s)

# Style is (fgcolor, bgcolor, font)
# Rudimentary: prints a single line.
def print_left(tft, x, y, s, style, tab=32):
    if s == '':
        return
    tft.text_style(style)
    tft.set_text_pos(x, y)
    font = style[2]
    if isinstance(font, IFont):  # Tabs unsupported for internal fonts
        return font.render(tft, x, y, s, style)
    tft.print_string(s, tab=tab)

# *********** LCD160CR_G CLASS ************


# Subclass LCD160CR to enable greying out of controls and to provide extra methods
class LCD160CR_G(LCD160CR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'bufsize' in kwargs:
            bs = kwargs['bufsize']
        else:
            bs = 1058  # font14 is 23*23 pixels
        self.glyph_buf = bytearray(bs)
        self._is_grey = False
        self.dim(2)  # Default grey-out: dim colors by factor of 2
        self.desaturate(True)
        # Default colors. These never change. They serve as global defaults.
        # bgcolor is also used to blank screen areas.
        self.fgcolor = (WHITE)
        self.bgcolor = (BLACK)
        self.text_fgcolor = self.fgcolor # colors set by user
        self.text_bgcolor = self.bgcolor
        self.text_fgc = self.fgcolor    # colors used by text rendering allowing for grey status
        self.text_bgc = self.bgcolor
        self.text_font = IFont(3)  # Default

    def get_fgcolor(self):
        return self.fgcolor

    def get_bgcolor(self):
        return self.bgcolor

    def _setcolor(self, color):
        if self._is_grey:
            color = self._greyfunc(color, self._factor)
        lf = self.rgb(*color)
        self.set_pen(lf, lf)  # line and fill colors are the same

    def desaturate(self, value=None):
        if value is not None:
            self._desaturate = value
            def do_dim(color, factor): # Dim a color
                if color is not None:
                    return tuple(int(x / factor) for x in color)

            def do_desat(color, factor): # Desaturate and dim
                if color is not None:
                    f = int(max(color) / factor)
                    return (f, f, f)
            # Specify the local function
            self._greyfunc = do_desat if value else do_dim
        return self._desaturate

    def dim(self, factor=None):
        if factor is not None:
            if factor <= 1:
                raise ValueError('Dim factor must be > 1')
            self._factor = factor
        return self._factor

    def usegrey(self, val): # tft.usegrey(True) sets greyed-out
        self._is_grey = val

    # self.rect() doesn't do the same thing - seems to draw > 1 pixel wide
    def draw_rectangle(self, x1, y1, x2, y2, color):
        self._setcolor(color)
        self.draw_hline(x1, y1, x2 - x1)
        self.draw_hline(x1, y2, x2 - x1)
        self.draw_vline(x1, y1, y2 - y1)
        self.draw_vline(x2, y1, y2 - y1)

    def fill_rectangle(self, x1, y1, x2, y2, color):
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        self._setcolor(color)
        self.rect(x1, y1, width, height)

    def draw_clipped_rectangle(self, x1, y1, x2, y2, color):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if (x2-x1) > 4 and (y2-y1) > 4:
            self._setcolor(color)
            self.dot(x1 + 2, y1 + 1)
            self.dot(x1 + 1, y1 + 2)
            self.dot(x2 - 2, y1 + 1)
            self.dot(x2 - 1, y1 + 2)
            self.dot(x1 + 2, y2 - 1)
            self.dot(x1 + 1, y2 - 2)
            self.dot(x2 - 2, y2 - 1)
            self.dot(x2 - 1, y2 - 2)
            self.draw_hline(x1 + 3, y1, x2 - x1 - 5)
            self.draw_hline(x1 + 3, y2, x2 - x1 - 5)
            self.draw_vline(x1, y1 + 3, y2 - y1 - 5)
            self.draw_vline(x2, y1 + 3, y2 - y1 - 5)

    def fill_clipped_rectangle(self, x1, y1, x2, y2, color):
        if x1 > x2:
            t = x1; x1 = x2; x2 = t
        if y1 > y2:
            t = y1; y1 = y2; y2 = t
        if (x2-x1) > 4 and (y2-y1) > 4:
            self._setcolor(color)
            for i in range(((y2 - y1) // 2) + 1):
                if i == 0:
                    self.draw_hline(x1 + 3, y1 + i, x2 - x1 - 5)
                    self.draw_hline(x1 + 3, y2 - i, x2 - x1 - 5)
                elif i == 1:
                    self.draw_hline(x1 + 2, y1 + i, x2 - x1 - 3)
                    self.draw_hline(x1 + 2, y2 - i, x2 - x1 - 3)
                elif i == 2:
                    self.draw_hline(x1 + 1, y1 + i, x2 - x1 - 1)
                    self.draw_hline(x1 + 1, y2 - i, x2 - x1 - 1)
                else:
                    self.draw_hline(x1, y1 + i, x2 - x1 + 1)
                    self.draw_hline(x1, y2 - i, x2 - x1 + 1)

    def draw_circle(self, x, y, radius, color):
        x = int(x)
        y = int(y)
        radius = int(radius)
        self._setcolor(color)
        f = 1 - radius
        ddF_x = 1
        ddF_y = -2 * radius
        x1 = 0
        y1 = radius

        self.dot(x, y + radius)
        self.dot(x, y - radius)
        self.dot(x + radius, y)
        self.dot(x - radius, y)

        while x1 < y1:
            if f >= 0:
                y1 -= 1
                ddF_y += 2
                f += ddF_y
            x1 += 1
            ddF_x += 2
            f += ddF_x
            self.dot(x + x1, y + y1)
            self.dot(x - x1, y + y1)
            self.dot(x + x1, y - y1)
            self.dot(x - x1, y - y1)
            self.dot(x + y1, y + x1)
            self.dot(x - y1, y + x1)
            self.dot(x + y1, y - x1)
            self.dot(x - y1, y - x1)

    # pen color has been set by caller
    def fill_circle(self, x, y, radius, color):
        self._setcolor(color)
        x = int(x)
        y = int(y)
        radius = int(radius)
        r_square = radius * radius * 4
        for y1 in range (-(radius * 2), 1):
            y_square = y1 * y1
            for x1 in range (-(radius * 2), 1):
                if x1 * x1 + y_square <= r_square:
                    x1i = x1 // 2
                    y1i = y1 // 2
                    self.draw_hline(x + x1i, y + y1i, 2 * -x1i)
                    self.draw_hline(x + x1i, y - y1i, 2 * -x1i)
                    break;

    # Save and restore a rect region to a 16 bit array.
    # Regions are inclusive of start and end (to match fill_rectangle)

    def save_region(self, buf, x0, y0, x1, y1):
        self.screen_dump(buf, x0, y0, x1 - x0 + 1, y1 - y0 + 1)

    # 1.1ms
    def restore_region(self, buf, x0, y0, x1, y1):
        self.set_spi_win(x0, y0, x1 - x0 + 1, y1 - y0 + 1)
        self.show_framebuf(buf)

    def set_text_pos(self, x, y):
        self.text_y = y
        self.text_x = x

    # Get or set the text style (fgcolor, bgcolor, font)
    # colors are (r, g, b)
    # Sets self.text_bgc and self.text_fgc for rendering methods
    def text_style(self, style=None):
        if style is not None:
            if self._is_grey:
                self.text_bgc = self._greyfunc(style[1], self._factor)
            else:
                self.text_bgc = style[1]
            self.text_fgc = style[0]

            font = style[2]
            if not isinstance(font, IFont):
                if not font.hmap():
                    raise UguiException('Font must be horizontally mapped')
                if font.height() * font.max_width() * 2 > len(self.glyph_buf):
                    raise UguiException('Font too large for buffer')
            self.text_font = font  # colors allow for disabled status

            return (self.text_fgc, self.text_bgc, self.text_font)

        return (self.text_fgcolor, self.text_bgcolor, self.text_font)

    def _newline(self, rows):
        self.text_x = 0
        self.text_y += rows

    def print_char(self, c, wrap, fgcolor, bgcolor, tab=32):
# get the character's pixel bitmap and dimensions
        if self.text_font:
            glyph, rows, cols = self.text_font.get_ch(c)
        else:
            raise AttributeError('No font selected')
        if c == '\n':
            self._newline(rows)
            return 0
        if c == '\t':
            xs = self.text_x
            self.text_x += tab - self.text_x % tab
            return self.text_x - xs

# test char fit
        if wrap:
            if self.text_x + cols >= self.w: # does the glyph fit on the screen?
                self._newline(rows)         # wrap to next text row then print
        if self.text_x + cols >= self.w or self.text_y + rows >= self.h:
            return 0                        # Glyph is not entirely on screen
        fbuf = framebuf.FrameBuffer(self.glyph_buf, cols, rows, framebuf.RGB565)
        if fast_mode:
            buf = bytearray_at(addressof(glyph), len(glyph))  # Object with buffer protocol
            fbc = framebuf.FrameBuffer(buf, cols, rows, framebuf.MONO_HLSB)
            render(fbuf, fbc, 0, 0, fgcolor, bgcolor)
        else:
            div, mod = divmod(cols, 8)          # Horizontal mapping
            gbytes = div + 1 if mod else div    # No. of bytes per row of glyph
            for row in range(rows):
                for col in range(cols):
                    gbyte, gbit = divmod(col, 8)
                    if gbit == 0:               # Next glyph byte
                        data = glyph[row * gbytes + gbyte]
                    fbuf.pixel(col, row, fgcolor if data & (1 << (7 - gbit)) else bgcolor)

        self.set_spi_win(self.text_x, self.text_y, cols, rows)
        self.show_framebuf(fbuf)
        self.text_x += cols
        return cols

    def print_string(self, s, wrap=False, tab=32):
        fgcolor = self.rgb(*self.text_fgc)
        bgcolor = self.rgb(*self.text_bgc)
        length = 0
        for c in s:
            length += self.print_char(c, wrap, fgcolor, bgcolor, tab)
        return length

# Convenience methods to ease porting from TFT
# Draw a vertical line with 1 Pixel width, from x,y to x, y + l - 1
    def draw_vline(self, x, y, l, color=None):
        if color is not None:  # caller hasn't issued _setcolor
            self._setcolor(color)
        self.line(x, y, x, y + l -1)

# Draw a horizontal line with 1 Pixel width, from x,y to x + l - 1, y
    def draw_hline(self, x, y, l, color=None):
        if color is not None:  # caller hasn't issued _setcolor
            self._setcolor(color)
        self.line(x, y, x + l - 1, y)

    def draw_line(self, x1, y1, x2, y2, color=None):
        if color is not None:  # caller hasn't issued _setcolor
            self._setcolor(color)
        self.line(x1, y1, x2, y2)

    def clr_scr(self):
        self._setcolor((0, 0, 0))
        self.rect(0, 0, self.w, self.h)

# *********** BASE CLASSES ***********

class Screen:
    current_screen = None
    tft = None
    is_shutdown = asyncio.Event()

    @classmethod
    def setup(cls, lcd):
        cls.tft = lcd

# get_tft() when called from user code, ensure greyed_out status is updated.
    @classmethod
    def get_tft(cls, greyed_out=False):
        cls.tft.usegrey(greyed_out)
        return cls.tft

    @classmethod
    def set_grey_style(cls, *, desaturate=True, factor=2):
        cls.tft.dim(factor)
        cls.tft.desaturate(desaturate)
        if Screen.current_screen is not None: # Can call before instantiated
            for obj in Screen.current_screen.displaylist:
                if obj.visible and obj.greyed_out():
                    obj.redraw = True # Redraw static content
                    obj.draw_border()
                    obj.show()

    @classmethod
    def show(cls):
        for obj in cls.current_screen.displaylist:
            if obj.visible: # In a buttonlist only show visible button
                obj.redraw = True # Redraw static content
                obj.draw_border()
                obj.show()

    @classmethod
    def change(cls, cls_new_screen, *, forward=True, args=[], kwargs={}):
        init = cls.current_screen is None
        if init:
            Screen() # Instantiate a blank starting screen
        else:  # About to erase an existing screen
            for entry in cls.current_screen.tasklist:
                if entry[1]:  # To be cancelled on screen change
                    entry[0].cancel()
        cs_old = cls.current_screen
        cs_old.on_hide() # Optional method in subclass
        if forward:
            if type(cls_new_screen) is ClassType:
                new_screen = cls_new_screen(*args, **kwargs) # Instantiate new screen
            else:
                raise ValueError('Must pass Screen class or subclass (not instance)')
            new_screen.parent = cs_old
            cs_new = new_screen
        else:
            cs_new = cls_new_screen # An object, not a class
        cls.current_screen = cs_new
        cs_new.on_open() # Optional subclass method
        cs_new._do_open(cs_old) # Clear and redraw
        cs_new.after_open() # Optional subclass method
        if init:
            try:
                asyncio.run(Screen.monitor())
            finally:
                asyncio.new_event_loop()

    @classmethod
    async def monitor(cls):
        await cls.is_shutdown.wait()
        for entry in cls.current_screen.tasklist:
            entry[0].cancel()
        await asyncio.sleep_ms(0)  # Allow subclass to cancel tasks
        cls.current_screen = None  # Ensure another demo can run

    @classmethod
    def back(cls):
        parent = cls.current_screen.parent
        if parent is not None:
            cls.change(parent, forward = False)

    @classmethod
    def addobject(cls, obj):
        if cls.current_screen is None:
            raise OSError('You must create a Screen instance')
        if isinstance(obj, Touchable):
            cls.current_screen.touchlist.append(obj)
        cls.current_screen.displaylist.append(obj)

    @classmethod
    def shutdown(cls):
        cls.tft.clr_scr()
        cls.is_shutdown.set()
        cls.is_shutdown.clear()

    def __init__(self):
        self.touchlist = []
        self.displaylist = []
        self.tasklist = []  # Allow instance to register tasks for shutdown
        self.modal = False
        if Screen.current_screen is None: # Initialising class and coro
            tft = Screen.get_tft()
            if tft.text_font is None:
                raise UguiException('The lcd set_font method has not been called')
            asyncio.create_task(self._touchtest()) # One coro only
            asyncio.create_task(self._garbage_collect())
        Screen.current_screen = self
        self.parent = None

    async def _touchtest(self): # Singleton coro tests all touchable instances
        touch_panel = Screen.tft
        while True:
            await asyncio.sleep_ms(0)
            tl = Screen.current_screen.touchlist
            ids = id(Screen.current_screen)
            touched, x, y = touch_panel.get_touch()
            if touched:
                # The following fixes a problem with the driver/panel where the first
                # coordinates read are incorrect. Reading again after a delay seems to fix it
                await asyncio.sleep_ms(20)
                touched, xx, yy = touch_panel.get_touch()
                if touched:  # Still touched: update x and y with the latest values
                    x = xx
                    y = yy
                for obj in iter(a for a in tl if a.visible and not a.greyed_out()):
                    obj._trytouch(x, y)  # Run user "on press" callback if touched
                    if ids != id(Screen.current_screen):  # cb may have changed screen
                        break  # get new touchlist
            else:
                for obj in iter(a for a in tl if a.was_touched):
                    obj.was_touched = False # Call _untouched once only
                    obj.busy = False
                    obj._untouched()  # Run "on release" callback

    def _do_open(self, old_screen): # Aperture overrides
        show_all = True
        tft = Screen.get_tft()
# If opening a Screen from an Aperture just blank and redraw covered area
        if old_screen.modal:
            show_all = False
            x0, y0, x1, y1 = old_screen._list_dims()
            tft.fill_rectangle(x0, y0, x1, y1, tft.get_bgcolor()) # Blank to screen BG
            for obj in [z for z in self.displaylist if z.overlaps(x0, y0, x1, y1)]:
                if obj.visible:
                    obj.redraw = True # Redraw static content
                    obj.draw_border()
                    obj.show()
# Normally clear the screen and redraw everything
        else:
            tft.clr_scr()
            Screen.show()

    def on_open(self): # Optionally implemented in subclass
        return

    def after_open(self): # Optionally implemented in subclass
        return

    def on_hide(self): # Optionally implemented in subclass
        return

    def reg_task(self, task, on_change=False):  # May be passed a coro or a Task
        if isinstance(task, type_coro):
            task = asyncio.create_task(task)
        self.tasklist.append([task, on_change])

    async def _garbage_collect(self):
        while True:
            await asyncio.sleep_ms(100)
            gc.collect()
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

# Very basic window class. Cuts a rectangular hole in a screen on which content may be drawn
class Aperture(Screen):
    _value = None
    def __init__(self, location, height, width, *, draw_border=True, bgcolor=None, fgcolor=None):
        Screen.__init__(self)
        self.location = location
        self.height = height
        self.width = width
        self.draw_border = draw_border
        self.modal = True
        tft = Screen.get_tft()
        self.fgcolor = fgcolor if fgcolor is not None else tft.get_fgcolor()
        self.bgcolor = bgcolor if bgcolor is not None else tft.get_bgcolor()

    def locn(self, x, y):
        return (self.location[0] + x, self.location[1] + y)

    def _do_open(self, old_screen):
        tft = Screen.get_tft()
        x, y = self.location[0], self.location[1]
        tft.fill_rectangle(x, y, x + self.width, y + self.height, self.bgcolor)
        if self.draw_border:
            tft.draw_rectangle(x, y, x + self.width, y + self.height, self.fgcolor)
        Screen.show()

    def _list_dims(self):
        x0 = self.location[0]
        x1 = self.location[0] + self.width
        y0 = self.location[1]
        y1 = self.location[1] + self.height
        return x0, y0, x1, y1

    # Mechanism for passing the outcome of a modal dialog box to the calling screen.
    @classmethod
    def value(cls, val=None):
        if val is not None:
            cls._value = val
        return cls._value

# Base class for all displayable objects
class NoTouch:
    _greyed_out = False # Disabled by user code
    def __init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, value, initial_value):
        Screen.addobject(self)
        self.screen = Screen.current_screen
        self.redraw = True # Force drawing of static part of image
        self.location = location
        self._value = value
        self._initial_value = initial_value # Optionally enables show() method to handle initialisation
        self.fontcolor = WHITE if fontcolor is None else fontcolor
        self.height = height
        self.width = width
        self.fill = bgcolor is not None
        self.visible = True # Used by ButtonList class for invisible buttons
#        self._greyed_out = False # Disabled by user code
        tft = Screen.get_tft(False) # Not greyed out
        if font is None:
            self.font = tft.text_font
        else:
            self.font = font

        if fgcolor is None:
            self.fgcolor = tft.get_fgcolor()
            if bgcolor is None:
                self.bgcolor = tft.get_bgcolor()
            else:
                self.bgcolor = bgcolor
            self.fontbg = self.bgcolor
        else:
            self.fgcolor = fgcolor
            if bgcolor is None:
                self.bgcolor = tft.get_bgcolor()  # black surround to circle button etc
                self.fontbg = fgcolor  # Fonts are drawn on bg of foreground color
            else:
                self.bgcolor = bgcolor
                self.fontbg = bgcolor

        self.text_style = tft.text_style((self.fontcolor, self.fontbg, self.font))
        self.border = 0 if border is None else int(max(border, 0)) # width
        self.bdcolor = self.fgcolor  # Border is always drawn in original fgcolor
        self.callback = dolittle # Value change callback
        self.args = []
        self.cb_end = dolittle # Touch release callbacks
        self.cbe_args = []

    @property
    def tft(self):
        return Screen.get_tft(self._greyed_out)

    def greyed_out(self):
        return self._greyed_out # Subclass may be greyed out

    def value(self, val=None, show=True): # User method to get or set value
        if val is not None:
            if type(val) is float:
                val = min(max(val, 0.0), 1.0)
            if val != self._value:
                self._value = val
                self._value_change(show)
        return self._value

    def _value_change(self, show): # Optional override in subclass
        self.callback(self, *self.args) # CB is not a bound method. 1st arg is self
        if show:
            self.show_if_current()

    def show_if_current(self):
        if self.screen is Screen.current_screen:
            self.show()

# Called by Screen.show(). Draw background and bounding box if required
    def draw_border(self):
        if self.screen is Screen.current_screen:
            tft = self.tft
            x = self.location[0]
            y = self.location[1]
            if self.fill:
                tft.fill_rectangle(x, y, x + self.width, y + self.height, self.bgcolor)
            if self.border > 0: # Draw a bounding box
                tft.draw_rectangle(x, y, x + self.width, y + self.height, self.bdcolor)
        return self.border # border width in pixels

    def overlaps(self, xa, ya, xb, yb): # Args must be sorted: xb > xa and yb > ya
        x0 = self.location[0]
        y0 = self.location[1]
        x1 = x0 + self.width
        y1 = y0 + self.height
        if (ya <= y1 and yb >= y0) and (xa <= x1 and xb >= x0):
            return True
        return False

# Base class for touch-enabled classes.
class Touchable(NoTouch):
    def __init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, can_drag, value, initial_value):
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, value, initial_value)
        self.can_drag = can_drag
        self.busy = False
        self.was_touched = False

    def _set_callbacks(self, cb, args, cb_end=None, cbe_args=None):
        self.callback = cb
        self.args = args
        if cb_end is not None:
            self.cb_end = cb_end
            self.cbe_args = cbe_args

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            tft = self.tft
            tft.usegrey(val)
            self._greyed_out = val
            self.draw_border()
            self.redraw = True
            self.show_if_current()
        return self._greyed_out

    def _trytouch(self, x, y): # If touched in bounding box, process it otherwise do nothing
        x0 = self.location[0]
        x1 = self.location[0] + self.width
        y0 = self.location[1]
        y1 = self.location[1] + self.height
        if x0 <= x <= x1 and y0 <= y <= y1:
            self.was_touched = True  # Cleared by Screen._touchtest
            if not self.busy or self.can_drag:
                self._touched(x, y) # Called repeatedly for draggable objects
                self.busy = True # otherwise once only

    def _untouched(self): # Default if not defined in subclass
        self.cb_end(self, *self.cbe_args) # Callback not a bound method so pass self
