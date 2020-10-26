# pad.py Extension to lcd160gui providing the invisible touchpad class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Usage: import classes as required:
# from gui.widgets.pad import Pad

import uasyncio as asyncio

from gui.core.lcd160_gui import Touchable
from gui.primitives.delay_ms import Delay_ms

# Pad coordinates relate to bounding box (BB). x, y are of BB top left corner.
# likewise width and height refer to BB

class Pad(Touchable):
    long_press_time = 1000
    def __init__(self, location, *, height=20, width=50, onrelease=True,
                 callback=None, args=[], lp_callback=None, lp_args=[]):
        super().__init__(location, None, height, width, None, None, None, None, False, '', None)
        self.callback = callback
        self.callback_args = args
        self.onrelease = onrelease
        self.lp_callback = lp_callback
        self.lp_args = lp_args
        self.lp_task = None # Long press not in progress

    def show(self):
        pass

    def _touched(self, x, y):  # Process touch
        if self.lp_callback is not None:
            self.lp_task = asyncio.create_task(self.longpress())
        if not self.onrelease and self.callback is not None:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    def _untouched(self):
        if self.lp_task is not None:
            self.lp_task.cancel()
            self.lp_task = None
        if self.onrelease and self.callback is not None:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    async def longpress(self):
        await asyncio.sleep_ms(Pad.long_press_time)
        self.lp_callback(self, *self.lp_args)
