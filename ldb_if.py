# ldb.py Test/demo of modal dialog box for Pybboard LCD160CR GUI

# The MIT License (MIT)
#
# Copyright (c) 2016 Peter Hinch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from constants import *
from lcd160_gui import Button, Label, Screen, Aperture, DialogBox, IFont
from lcd_local import setup
# STANDARD BUTTONS

font3 = IFont(3)

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font3, callback = quit, fgcolor = RED, text = 'Quit',)

def fwdbutton(x, y, cls_screen, *, text='Next', args=[], kwargs={}):
    def fwd(button):
        Screen.change(cls_screen, args = args, kwargs = kwargs)
    Button((x, y), font = font3, callback = fwd, fgcolor = RED, text = text)

# Demo of creating a dialog manually
class UserDialogBox(Aperture):
    def __init__(self):
        height = 80
        width = 130
        super().__init__((20, 20), height, width, bgcolor = DARKGREEN)
        y = self.height - 30
        Button(self.locn(10, y), font = font3, fontcolor = BLACK, fgcolor = RED,
               text = 'Cat',  callback = self.back, args = ('Cat',))
        Button(self.locn(70, y), font = font3, fontcolor = BLACK, fgcolor = GREEN,
               text = 'Dog', callback = self.back, args = ('Dog',))
        Button(self.locn(width - 21, 1), height = 20, width = 20, font = font3,
               fgcolor = RED,  text = 'X', callback = self.back, args = ('Close',))

    def back(self, button, text):
        Aperture.value(text)
        Screen.back()

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font3, value = 'Dialog box demo.')
        Label((0, 20), font = font3, value = 'User written and')
        Label((0, 40), font = font3, value = 'auto generated')
        self.lbl_result = Label((0, 80), font = font3, fontcolor = WHITE, width = 70,
                                border = 2, fgcolor = RED, bgcolor = DARKGREEN)
# User written dialog
        fwdbutton(54, 107, UserDialogBox, text = 'User')
# Dialog built using DialogBox class
        dialog_elements = (('Yes', GREEN), ('No', RED), ('Foo', YELLOW))
        fwdbutton(0, 107, DialogBox, text = 'Gen', args = (font3,),
                  kwargs = {'elements' : dialog_elements, 'label' : 'Test dialog'})
        quitbutton()

    def on_open(self):
        self.lbl_result.value(Aperture.value())

def test():
    setup()
    Screen.change(BaseScreen)

test()
