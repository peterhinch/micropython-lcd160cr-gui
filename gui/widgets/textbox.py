# textbox.py Extension to lcd160gui providing the Textbox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

from gui.core.lcd160_gui import Touchable, IFont, print_left

class Textbox(Touchable):
    def __init__(self, location, width, nlines, font, *, border=2, fgcolor=None,
                 bgcolor=None, fontcolor=None, clip=True, repeat=True, tab=32):
        height = nlines * font.height() + 2 * border if isinstance(border, int) else nlines * font.height()
        super().__init__(location, font, height, width, fgcolor, bgcolor,
                         fontcolor, border, repeat, 0, 0)
        self.nlines = nlines
        self.clip = clip
        self.tab = tab
        self.lines = []
        self.start = 0  # Start line for display

    def _add_lines(self, s):
        width = self.width - 2 * self.border
        font = self.text_style[2]
        n = -1  # Index into string
        newline = True
        while True:
            n += 1
            if newline:
                newline = False
                ls = n  # Start of line being processed
                col = 0  # Column relative to text area
            if n >= len(s):  # End of string
                if n > ls:
                    self.lines.append(s[ls :])
                return
            c = s[n]  # Current char
            if c == '\n':
                self.lines.append(s[ls : n])
                newline = True
                continue  # Line fits window
            if c == '\t':
                col += self.tab - col % self.tab
            elif isinstance(font, IFont):  # Monospaced
                col += font.width
            else:
                col += font.get_ch(c)[2]  # width of current char
            if col > width:
                if self.clip:
                    p = s[ls :].find('\n')  # end of 1st line
                    if p == -1:
                        self.lines.append(s[ls : n])  # clip, discard all to right
                        return
                    self.lines.append(s[ls : n])  # clip, discard to 1st newline
                    n = p  # n will move to 1st char after newline
                elif c == ' ':  # Easy word wrap
                    self.lines.append(s[ls : n])
                else:  # Edge splits a word
                    p = s.rfind(' ', ls, n + 1)
                    if p >= 0:  # spacechar in line: wrap at space
                        assert (p > 0), 'space char in position 0'
                        self.lines.append(s[ls : p])
                        n = p
                    else:  # No spacechar: wrap at end
                        self.lines.append(s[ls : n])
                        n -= 1  # Don't skip current char
                newline = True

    def _print_lines(self):
        if len(self.lines):
            tft = self.tft
            bw = self.border
            x = self.location[0] + bw
            y = self.location[1] + bw
            xstart = x  # Print the last lines that fit widget's height
            font = self.text_style[2]
            #for line in self.lines[-self.nlines : ]:
            for line in self.lines[self.start : self.start + self.nlines]:
                print_left(tft, x, y, line, self.text_style, self.tab)
                y += font.height()
                x = xstart

    def show(self):
        tft = self.tft
        bw = self.border
        x, y = self.location
        w = self.width
        # Clear text area
        tft.fill_rectangle(x + bw, y + bw, x + w - bw, y + self.height - bw, self.bgcolor)
        self._print_lines()

    def append(self, s, ntrim=None, line=None):
        self._add_lines(s)
        if ntrim is None:  # Default to no. of lines that can fit
            ntrim = self.nlines
        if len(self.lines) > ntrim:
            self.lines = self.lines[-ntrim:]
        self.goto(line)

    def scroll(self, n):  # Relative scrolling
        value = len(self.lines)
        if n == 0 or value <= self.nlines:
            return
        s = self.start
        self.start = max(0, min(self.start + n, value - self.nlines))
        if s != self.start:
            self.show_if_current()

    def _touched(self, x, y): # Was touched
        self.scroll(-1 if  2 * (y - self.location[1]) < self.height else 1)

    def value(self):
        return len(self.lines)

    def clear(self):
        self.lines = []
        self.show_if_current()

    def goto(self, line=None):  # Absolute scrolling
        if line is None:
            self.start = max(0, len(self.lines) - self.nlines)
        else:
            self.start = max(0, min(line, len(self.lines) - self.nlines))
        self.show_if_current()
