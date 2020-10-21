# dialog.py Extension to lcd160gui providing the DialogBox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

from core.lcd160_gui import Aperture, Screen, get_stringsize, dolittle
from widgets.label import Label
from widgets.buttons import Button
from core.constants import * 

# Usage:
# from widgets.dialog import DialogBox

# *********** DIALOG BOX CLASS ***********
# Enables parameterised creation of button-based dialog boxes. See ldb.py

class DialogBox(Aperture):
    def __init__(self, font, *, elements, location=(20, 20), label=None,
                 bgcolor=DARKGREEN, buttonwidth=25, closebutton=True):
        height = 100
        spacing = 5
        buttonwidth = max(max([get_stringsize(x[0], font)[0] for x in elements]) + 4, buttonwidth)
        buttonheight = max(get_stringsize('x', font)[1], 20)
        nelements = len(elements)
        width = spacing + (buttonwidth + spacing) * nelements
        if label is not None:
            width = max(width, get_stringsize(label, font)[0] + 2 * spacing)
        super().__init__(location, height, width, bgcolor = bgcolor)
        x = self.location[0] + spacing # Coordinates relative to physical display
        gap = 0
        if nelements > 1:
            gap = ((width - 2 * spacing) - nelements * buttonwidth) // (nelements - 1)
        y = self.location[1] + self.height - buttonheight - 10
        if label is not None:
            Label((x, self.location[1] + 25), font = font, bgcolor = bgcolor, value = label)
        for text, color in elements:
            Button((x, y), height = buttonheight, width = buttonwidth, font = font, fontcolor = BLACK, fgcolor = color,
                text = text, shape = RECTANGLE,
                callback = self.back, args = (text,))
            x += buttonwidth + gap
        if closebutton:
            x, y = get_stringsize('X', font)
            size = max(x, y, 20)
            Button((self.location[0] + width - (size + 1), self.location[1] + 1), height = size, width = size, font = font,
                fgcolor = RED,  text = 'X', shape = RECTANGLE,
                callback = self.back, args = ('Close',))

    def back(self, button, text):
        Aperture.value(text)  # Save value for calling screen
        Screen.back()
