# A touch GUI for the official MicroPython display

v0.21 29th Oct 2020 Add `Scale` and `Pad` widgets.  
V0.20 21st Oct 2020 Refactor as a Python package. The refactor is a breaking
change: applications must adapt `import` statements. There is now no need to
cross compile on a Pyboard 1.1. Unused widgets no longer consume RAM. The
structure also facilitates adding new widgets. Supports Jim Mussared's fast
text rendering.  
V0.12 21st Sep 2020 Updated for (and requires) uasyncio V3.  

Provides a simple touch driven event based GUI interface for the the official
LCD160CR colour display. It is based on the official driver and uses `uasyncio`
for scheduling. It has been tested on:
 * Pyboard 1.0 and 1.1
 * Pyboard D
 * ESP32
It should be easy to port to platforms having both I2C and SPI interfaces,
given sufficient RAM. The V1.1 display enables a Pyboard D to be plugged in to
the rear. The GUI has been tested in this configuration.

It is targeted at hardware control and display applications. GUI objects are
drawn using graphics primitives rather than by rendering bitmap images. This
ensures that they are scalable. The API is via event driven callbacks.

The library can use the fonts internal to the device and also arbitrary fonts
converted from `ttf` or `otf` formats.

An extension for plotting simple graphs is described [here](./LPLOT.md).

Images from the supplied test programs:

![Image](images/IMG_2501.JPG) ![Image](images/IMG_2502.JPG)  
Screen selection buttons. Two styles of checkboxes.  

![Image](images/IMG_2503.JPG) ![Image](images/IMG_2504.JPG)  
Assorted pushbutton styles. Radio buttons (1 of N selection).  

![Image](images/IMG_2505.JPG)  
Highlight buttons change color for a period after touching.  

![Image](images/IMG_2507.JPG) ![Image](images/IMG_2506.JPG)  
Slider controls allow control and display of float values. Also Meter, LED
and Dial displays.   

![Image](images/IMG_3250.JPG)  
The `Scale` control can accurately display variables having a wide range of
values. The scale moves within a window so that the current value aligns with
the fixed pointer. The scale color can change dynamically (in the lower
instance).

![Image](images/IMG_2513.JPG)  
Rotary controls and displays - `lkt.py` demonstrates the two styles of
"greying out" disabled controls.  

![Image](images/IMG_3251.JPG) ![Image](images/IMG_3252.JPG)  
Vector displays. These can display an arbitrary number of vectors in "clock" or
"compass" formats. Angle, length and color can change dynamically.

![Image](images/IMG_2511.JPG) ![Image](images/IMG_2512.JPG)  
Listbox and dropdown list objects (image on right shows dropdown opened).  

![Image](images/textbox1.JPG) ![Image](images/textbox2.JPG)  
The Textbox control displays scrolling text in a window. Supports tabs with
variable pitch fonts. Text can be scrolled by touch or programmatically. Text
may be clipped or word-wrapped.

![Image](images/IMG_2509.JPG)  
A modal dialog box.  

![Image](images/IMG_2514.JPG) ![Image](images/IMG_2515.JPG)  
The Plot module: Cartesian and polar graphs.

# Contents

1. [Pre requisites](./README.md#1-pre-requisites)  
  1.1 [Pre installation](./README.md#11-pre-installation)  
  1.2 [Library Documentation](./README.md#12-library-documentation)  
  1.3 [Installation](./README.md#13-installation)  
  1.4 [Dependencies and Python files](./README.md#14-dependencies-and-python-files)  
  1.5 [A performance boost](./README.md#15-a-performance-boost)  
2. [Concepts](./README.md#2-concepts)  
  2.1 [Terminology](./README.md#21-terminology)  
  2.2 [Coordinates](./README.md#22-coordinates)  
  2.3 [Colors](./README.md#23-colors)  
  2.4 [Callbacks](./README.md#24-callbacks)  
  2.5 [Screens](./README.md#25-screens)  
3. [Program Structure](./README.md#3-program-structure)  
  3.1 [Initialisation](./README.md#31-initialisation)  
4. [Class Screen](./README.md#4-class-screen)  
  4.1 [Class methods](./README.md#41-class-methods)  
  4.2 [Constructor](./README.md#42-constructor)  
  4.3 [Callback methods](./README.md#43-callback-methods)  
  4.4 [Method](./README.md#44-method)  
5. [Display Classes](./README.md#5-display-classes)  
  5.1 [Class Label](./README.md#51-class-label) Display static or dynamic text.  
  5.2 [Class Dial](./README.md#52-class-dial) Rotary display of variables.  
  5.3 [Class LED](./README.md#53-class-led) On/off display.  
  5.4 [Class Meter](./README.md#54-class-meter) Linear "panel meter" device.  
  5.5 [Vector display](./README.md#55-vector-display) Compass and clock style display of multiple vectors.  
  5.6 [Scale class](./README.md#56-scale-class) Linear display with wide dynamic range.  
6. [Control Classes](./README.md#6-control-classes)  
  6.1 [Class Button](./README.md#61-class-button)  
  6.2 [Class ButtonList: emulate a button with multiple states](./README.md#62-class-buttonlist-emulate-a-button-with-multiple-states)  
  6.3 [Class RadioButtons](./README.md#63-class-radiobuttons)  
  6.4 [Class Slider](./README.md#64-class-slider)  
  6.5 [Class Knob](./README.md#65-class-knob)  
  6.6 [Class Checkbox](./README.md#66-class-checkbox)  
  6.7 [Class Listbox](./README.md#67-class-listbox)  
  6.8 [Class Dropdown](./README.md#68-class-dropdown)  
  6.9 [Class Pad](./README.md#69-class-pad) Invisible touch sensitive region.  
  6.10 [Class Textbox](./README.md#610-class-textbox) Scrolling text display with tab support.  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.10.1 [Note on tabs](./README.md#6101-note-on-tabs)  
7. [Dialog Boxes](./README.md#7-dialog-boxes)  
  7.1 [Class Aperture](./README.md#71-class-aperture)  
  7.2 [Class DialogBox](./README.md#72-class-dialogbox)  
8. [Fonts](./README.md#8-fonts)  
  8.1 [External fonts](./README.md#81-external-fonts)  
  8.2 [Internal fonts: Class IFont](./README.md#82-internal-fonts-class-ifont)  
9. [Issues](./README.md#9-issues) A problem encountered with old LCD160CR firmware  
10. [Application design note](./README.md#10-application-design-note) Touch application design  
11. [ESP32](./README.md#11-esp32) Use with non-Pyboard targets  

# 1. Pre requisites

Firmware should be V1.13 or later.

## 1.1 Pre installation

Before running the GUI the hardware should be tested by working through the
[tutorial](https://docs.micropython.org/en/latest/pyboard/pyboard/tutorial/lcd160cr_skin.html).

Familiarity with callbacks and event driven programming will assist in
developing applications. No knowledge of `uasyncio` is required for application
development as the API is callback-based, but the GUI is compatible with
`uasyncio` applications.

## 1.2 Library Documentation

Documentation for the underlying libraries may be found at these sites.  

[lcd160cr driver](http://docs.micropython.org/en/latest/pyboard/library/lcd160cr.html#touch-screen-methods)  

Other references:  
[Font format](https://github.com/peterhinch/micropython-font-to-py)  
[uasyncio tutorial](https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md)  

## 1.3 Installation

The file `lcd_local.py` defines the hardware connection and should be edited to
match your hardware. On Pyboard D plugged into the back of a display select the
"X" connection. Edit if you plan to use fonts bigger than 23*23 pixels. See
[External fonts](./README.md#81-external-fonts).

Copy the following files to the root directory on the target (on Pyboard
`/flash` or `/sd`):
 1. `lcd_local.py`
 2. `font6.py` (Font files not required if frozen as bytecode).
 3. `font10.py`

Copy the `gui` directory and contents to the root directory on the target. If
using [rshell](https://github.com/dhylands/rshell) this may be done from the
directory containing `gui` with:
```bash
> rsync gui /sd/gui
```

For use with non-Pyboard targets, including ESP32, see 
[ESP32](./README.md#11-esp32).

## 1.4 Dependencies and Python files

Version 3 of uasyncio is included in firmware V1.13 and later. This is a
requirement.

Files in top level directory:
 1. `lcd_local.py`
 2. `font6.py` Font file used in demos.
 3. `font10.py` Ditto.
 4. `font14.py` Unused example of max font size using unmodified `lcd_local`.

Fonts are generated from the free font FreeSans.ttf. You can generate your own,
see [External fonts](./README.md#81-external-fonts).

Core files in `core` subdirectory:
 1. `lcd160cr.py` Official driver. Check for a newer version in the source tree
 (`drivers/display`).
 2. `lcd160_gui.py` The micro GUI library.
 3. `constants.py` Constants such as colors and shapes (import using
 `from gui.core.constants import *`).
 4. `lplot.py` Optional graph plotting extension.

Test/demo programs in `demos` subdirectory:
 1. `lvst.py` A test program for vertical linear sliders. Also demos an
 asynchronous coroutine and linked sliders.
 2. `lhst.py` Tests horizontal slider controls, meter and LED. Demos
 asynchronous coroutine, linked sliders and dynamically changing object colors.
 3. `lbt.py` Pushbuttons, radio buttons, highlighting buttons and checkboxes.
 "Reset" buttons respond to short and long presses.
 4. `lkt.py` Rotary controls. Shows the two styles of "greying out" of
 disabled controls.
 5. `ldd.py` Dropdown list and Listbox controls.
 6. `ldb.py` Modal dialog boxes.
 7. `ldb_if.py` As above but using an internal font.
 8. `lpt.py` Demo of plot module.
 9. `lptg.py` Plot with `TSequence` simulated real time data acquisition.
 10. `vtest.py` Test of vector display.
 11. `lscale.py` Demo of `Scale` object. This is capable of displaying floats
 to a high degree of accuracy.
 12. `tbox.py` Demo of `Textbox` class for scrolling text.

Synchronisation primitives in `primitives` subdirectory.  
Widgets in `widgets` subdirectory.

Demos are run with the following syntax:
```python
>>> import gui.demos.lbt
```
The organisation as a Python package means that cross compilation of
`lcd160_gui.py` is no longer required on a Pyboard 1.1. To conserve RAM it is
recommended that font files are implemented as frozen bytecode. To further
reduce RAM this may be applied to other Python files, but the directory
structure must be maintained.

## 1.5 A performance boost

This will only make a visible difference to applications rendering substantial
amounts of text using Python fonts.

Rendering Python fonts is slow as it is performed pixel by pixel. A potential
speedup is to use the `framebuf.blit` method but as standard it cannot render
monochrome objects to color displays. A fix for this was developed by Jim
Mussared (@jimmo) and consists of a native C module.

On import, `lcd160_gui.py` attempts to import a module `framebuf_utils`. If
this succeeds (i.e. a file `framebuf_utils.mpy` is found), rendering will be
substantially faster.

The directory `framebuf_utils` contains the source file, the makefile and a
version of `framebuf_utils.mpy` for `armv7m` architecture (e.g. Pyboards). To
install copy the directory and its contents to your device. On initialisation
the message "Using fast mode" will be printed at the REPL.

On other architectures `framebuf_utils.mpy` should be recompiled or deleted to
disable fast mode.

###### [Jump to Contents](./README.md#contents)

# 2. Concepts

## 2.1 Terminology

GUI objects are created on a `Screen` instance which normally fills the
entire physical screen. Displayable GUI objects comprise `control` and
`display` instances. The former can respond to touch (e.g. `Pushbutton`
instances) while the latter cannot (`LED` or `Dial` instances).

## 2.2 Coordinates

In common with most displays, the top left hand corner of the display is (0, 0)
with increasing values of x to the right, and increasing values of y downward.
Display objects exist within a rectangular bounding box; in the case of touch
sensitive controls this corresponds to the sensitive region. Locations are
defined as a 2-tuple (x, y). The location of an object is defined as the
location of the top left hand corner of the bounding box.

## 2.3 Colors

These are defined as a 3-tuple (r, g, b) with values of red, green and blue in
range 0 to 255. The interface and this document uses the American spelling
(color) throughout. This is for historical reasons.

## 2.4 Callbacks

The interface is event driven. Controls may have optional callbacks which will
be executed when a given event occurs. A callback function receives positional
arguments. The first is a reference to the object raising the callback.
Subsequent arguments are user defined, and are specified as a tuple or list of
items. Callbacks are optional, as are the argument lists - a default null
function and empty list are provided. Callbacks are usually bound methods - see
the Screens section for a reason why this is useful.

All controls and displays have a `tft` property which is the `LCD160CR_G`
instance. This enables callbacks to access drawing primitives.

## 2.5 Screens

GUI controls and displays are rendered on a `Screen` instance. A user program
may instantiate multiple screens, each with its own set of GUI objects. The
`Screen` class has class methods enabling runtime changes of the screen to be
rendered to the physical display. This enables nested screens. The feature is
demonstrated in `lbt.py`.

Applications should be designed with a `Screen` subclass for each of the
application's screens (even if the app uses only a single screen). This
faciitates sharing data between GUI objects on a screen, and simplifies the
handling of control callbacks. These will be methods bound to the user screen.
They can access the screen's bound variables via `self` and the control's
bound methods via the callback's first argument (which is a reference to the
control). Again `lbt.py` provides examples.

The `Screen` class has 3 null methods which may be implemented in subclasses:
`on_open` which runs when a screen is opened but prior to its display,
`after_open` which is called after display, and `on_hide` which runs when a
screen change is about to make the screen disappear. These may be used to
instantiate or control threads and to retrieve the results from a modal dialog
box.

The `Screen` class is configured in `lcd_local.py`.

###### [Jump to Contents](./README.md#contents)

# 3. Program Structure

The following illustrates the structure of a minimal program:
```python
from lcd_local import setup
import font10
from gui.core.constants import *
from gui.core.lcd160_gui import Screen
from gui.widgets.buttons import Button
def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE)

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        quitbutton()
setup()
Screen.change(BaseScreen)
```

The last line causes the Screen class to instantiate your `BaseScreen` and to
start the scheduler using that screen object. Control then passes to the
scheduler: the code following this line will not run until the GUI is shut down
and the scheduler is stopped (`Screen.shutdown()`).

## 3.1 Initialisation

This is performed by `lcd_local.py` which instantiates an `LCD160CR_G`
display. This class is derived from the official driver's `LCD160CR` class:
the documentation for the latter may be viewed
[here](http://docs.micropython.org/en/latest/library/lcd160cr.html).
An additional optional constructor keyword argument `bufsize` is available.
See [External fonts](./README.md#81-external-fonts) for its use.

###### [Jump to Contents](./README.md#contents)

# 4. Class Screen

The `Screen` class presents a full-screen canvas onto which displayable
objects are rendered. Before instantiating GUI objects a `Screen` instance
must be created. This will be current until another is instantiated. When a GUI
object is instantiated it is associated with the current screen.

The best way to use the GUI, even in single screen programs, is to create a
user screen by subclassing the `Screen` class. GUI objects are instantiated
in the constructor. This arrangement facilitates communication between objects
on the screen. The following presents an outline of this approach:

```python
from lcd_local import setup
import font10
from gui.core.constants import *
from gui.core.lcd160_gui import Screen
from gui.widgets.buttons import Button
from gui.widgets.label import Label
def backbutton(x, y):
    def back(button):
        Screen.back()
    Button((x, y), font = font10, fontcolor = BLACK, callback = back,
           fgcolor = CYAN,  text = 'Back')

def fwdbutton(x, y, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)
    Button((x, y), font = font10, callback = fwd, fgcolor = RED, text = text)

def quitbutton():
    def quit(button):
        Screen.shutdown()
    Button((109, 107), font = font10, callback = quit, fgcolor = RED, text = 'Quit')

class Screen_1(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font10, value = 'Test screen 1')
        backbutton(0, 100)

class Screen_0(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font10, value = 'Test screen 0')
        fwdbutton(0, 107, Screen_1)
        quitbutton()
setup()
Screen.change(Screen_0)
```

Note that the GUI is started by issuing `Screen.change` with the class as its
argument rather than an instance. This aims to minimise RAM usage.

## 4.1 Class methods

In normal use the following methods only are required:  
 * `change` Change screen, refreshing the display. Mandatory positional
 argument: the new screen class name. This must be a class subclassed from
 `Screen`. The class will be instantiated and displayed. Optional keyword
 arguments: `args`, `kwargs`. These enable passing positional and keyword
 arguments to the constructor of the new screen.
 * `back` Restore previous screen.
 * `shutdown` Clear the screen and shut down the GUI.
 * `set_grey_style` Sets the way in which disabled ('greyed-out') objects are
 displayed. The colors of disabled objects are dimmed by a factor and
 optionally desaturated (turned to shades of grey). Optional keyword arguments:
 `desaturate` default `True` and `factor` default 2. A `ValueError`
 will result if `factor` is <= 1. The default style is to desaturate and dim
 by a factor of 2.

Other method:  
 * `get_tft` Return the `LCD160CR` instance. This allows direct drawing to
 the physical screen. Anything so drawn will be lost when the screen is
 changed. In normal use the `TFT` instance is acquired via a GUI object's
 `tft` property.

See `lbt.py` and `ldb.py` for examples of multi-screen design.

## 4.2 Constructor

This takes no arguments.

## 4.3 Callback Methods

These do nothing, and may be defined in subclasses if required.

 * `on_open` Called when a screen is instantiated but prior to display.
 * `after_open` Called after a screen has been displayed.
 * `on_hide` Called when a screen ceases to be current.

## 4.4 Method

 * `reg_task` args `task`, `on_change=False`. This is a convenience method for
 applications which use `uasyncio` and provides for the automatic cancellation
 of tasks. The first arg may be a `Task` instance or a coroutine. If a `Screen`
 runs associated coros it can opt to register these. On shudown, any registered
 tasks of the base screen are cancelled. On screen change, registered tasks
 with `on_change` `True` are cancelled. For finer control applications can
 ignore this method and handle cancellation explicitly in code.

###### [Jump to Contents](./README.md#contents)

# 5. Display Classes

These classes provide ways to display data and are not touch sensitive.

## 5.1 Class Label

Displays text in a fixed length field. The height of a label is determined by
the metrics of the specified font.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Keyword only arguments:  
 * `font` Mandatory. Font object to use.
 * `width` The width of the object in pixels. Default: `None` - width is
 determined from the dimensions of the initial text.
 * `border` Border width in pixels - typically 2. If omitted, no border will
 be drawn.
 * `fgcolor` Color of border. Defaults to system color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `fontcolor` Text color. Defaults to system text color.
 * `value` Initial text. Default: `None`.

Method:
 * `value` Argument `val` string, default `None`. If provided, refreshes
 the label with the passed text otherwise clears the text in the label.

###### [Jump to Contents](./README.md#contents)

## 5.2 Class Dial

Displays angles in a circular dial. Angles are in radians with zero represented
by a vertical pointer. Positive angles appear as clockwise rotation of the
pointer. The object can display multiple angles using pointers of differing
lengths (like a clock face).

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Keyword only arguments (all optional):  
 * `height` Dimension of the square bounding box. Default 50 pixels.
 * `fgcolor` Color of border. Defaults to system color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `border` Border width in pixels - typically 2. If omitted, no border will
 be drawn.
 * `pointers` Tuple of floats in range 0 to 0.9. Defines the length of each
 pointer as a  proportion of the dial diameter. Default (0.9,) i.e. one pointer
 of length 0.9.
 * `ticks` Defines the number of graduations around the dial. Default 4.

Method:
 * `value` Arguments: `angle` (mandatory), `pointer` (optional) the
 pointer index. Displays  an angle. A `ValueError` will be raised if the
 pointer index exceeds the number of pointers defined by the constructor
 `pointers` argument.

###### [Jump to Contents](./README.md#contents)

## 5.3 Class LED

Displays a boolean state. Can display other information by varying the color.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Keyword only arguments (all optional):
 * `height` Dimension of the square bounding box. Default 20 pixels.
 * `fgcolor` Color of border. Defaults to system color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `border` Border width in pixels - default 2. If `None`, no border will
 be drawn.
 * `color` The color of the LED. Default RED.

Methods:
 * `value` Argument `val` boolean, default `None`. If provided, lights or
 extinguishes the LED. Always returns its current state.
 * `color` Argument `color`. Change the LED color without altering its
 state.

###### [Jump to Contents](./README.md#contents)

## 5.4 Class Meter

This displays a single value in range 0.0 to 1.0 on a vertical linear meter.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Keyword only arguments:
 * `height` Dimension of the bounding box. Default 100 pixels.
 * `width` Dimension of the bounding box. Default 26 pixels.
 * `font` Font to use in any legends. Default: `None` No legends will be
 displayed.
 * `legends` A tuple of strings to display on the centreline of the meter.
 These should be short to physically fit. They will appear equidistant along
 the vertical scale, with string 0 at the bottom. Default `None`: no legends
 will be shown.
 * `divisions` Count of graduations on the meter scale. Default 10.
 * `fgcolor` Color of border. Defaults to system color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `fontcolor` Text color. Defaults to system text color.
 * `pointercolor` Color of meter pointer. Defaults to `fgcolor`.
 * `value` Initial value to display. Default 0.

Methods:
 * `value` Optional argument `val`. If provided, refreshes the meter
 display with a new value. Range 0.0 to 1.0: out of range values will be
 constrained to full scale or 0. Always returns its current value. 

###### [Jump to Contents](./README.md#contents)

## 5.5 Vector display

Provides a means of displaying one or more vectors. A vector is a `complex`
with magnitude in the range of 0 to 1.0. In use a `VectorDial` is instantiated,
followed by a `Pointer` instance for each vector to be displayed on it. The
`VectorDial` can display its vectors as lines (as on a clock face) or as arrows
(as on a compass).

By contrast with the `Dial` class the pointers have lengths and colors which
can vary dynamically.
```python
from gui.widgets.vectors import Pointer, VectorDial
```

### Class VectorDial

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Keyword only arguments (all optional):  
 * `height=100` Dimension of the square bounding box.
 * `fgcolor=None` Foreground color. Defaults to system color.
 * `bgcolor=None` Background color of object. Defaults to system background.
 * `border=None` Border width in pixels - typically 2. Default: no border.
 * `ticks=4` Defines the number of graduations around the dial.
 * `arrow=False` If `True` vectors will appear as arrows.
 * `pip=None` By default a small circular "pip" is drawn at the centre of the
 dial. If `False` is passed this is omitted. If a color is passed, it will be
 drawn using that color. If the shortest pointer has a length below a threshold
 the "pip" is omitted to ensure visibility.

### Class Pointer

Constructor mandatory positional arg:
 * `dial` The dial on which it is to be displayed.

Method:
 * `value` Args `v=None, col=None`. Returns the current value. If a `complex`
 is passed as the value `v` it is scaled to ensure its magnitude is <= 1 and
 the pointer is redrawn. If a color is passed as `col` the pointer's color is
 updated.
 
###### [Jump to Contents](./README.md#contents)

## 5.6 Scale class

This displays floating point data having a wide dynamic range. It is modelled
on old radios where a large scale scrolls past a small window having a fixed
pointer. This enables a scale with (say) 200 graduations (ticks) to readily be
visible on a small display, with sufficient resolution to enable the user to
interpolate between ticks. Default settings enable estimation of a value to
within +-0.1%.

Legends for the scale are created dynamically as it scrolls past the window.
The user may control this by means of a callback. The example `lscale.py`
illustrates a variable with range 88.0 to 108.0, the callback ensuring that the
display legends match the user variable. A further callback enables the scale's
color to change over its length or in response to other circumstances.

The scale displays floats in range -1.0 <= V <= 1.0.

Constructor mandatory positional arguments:
 1. `location` 2-tuple defining position.
 2. `font` Font for labels.

Keyword only arguments (all optional): 
 * `ticks=200` Number of "tick" divisions on scale. Must be divisible by 2.
 * `legendcb=None` Callback for populating scale legends (see below).
 * `tickcb=None` Callback for setting tick colors (see below).
 * `height=0` Default is a minimum height based on the font height.
 * `width=100`
 * `border=2` Border width in pixels.
 * `fgcolor=None` Foreground color. Defaults to system color.
 * `bgcolor=None` Background color of object. Defaults to system background.
 * `pointercolor=None` Color of pointer. Defaults to `.fgcolor`.
 * `fontcolor=None` Color of legends. Default `WHITE`.
 * `value=0.0` Initial value.

Method:
 * `value=None` Set or get the current value. Always returns the current value.
 A passed `float` is constrained to the range -1.0 <= V <= 1.0 and becomes the
 `Scale`'s current value. The `Scale` is updated. Passing `None` enables
 reading the current value.

### Callback legendcb

The display window contains 20 ticks comprising two divisions; by default a
division covers a range of 0.1. A division has a legend at the start and end
whose text is defined by the `legendcb` callback. If no user callback is
supplied, legends will be of the form `0.3`, `0.4` etc. User code may override
these to cope with cases where a user variable is mapped onto the control's
range. The callback takes a single `float` arg which is the value of the tick
(in range -1.0 <= v <= 1.0). It must return a text string. An example from the
`lscale.py` demo shows FM radio frequencies:
```python
def legendcb(f):
    return '{:2.0f}'.format(88 + ((f + 1) / 2) * (108 - 88))
```
The above arithmetic aims to show the logic. It can be simplified.

### Callback tickcb

This callback enables the tick color to be changed dynamically. For example a
scale might change from green to orange, then to red as it nears the extremes.
The callback takes two args, being the value of the tick (in range 
-1.0 <= v <= 1.0) and the default color. It must return a color. This example
is taken from the `lscale.py` demo:
```python
def tickcb(f, c):
    if f > 0.8:
        return RED
    if f < -0.8:
        return BLUE
    return c
```

### increasing the ticks value

This increases the precision of the display.

It does this by lengthening the scale while keeping the window the same size,
with 20 ticks displayed. If the scale becomes 10x longer, the value diference
between consecutive large ticks and legends is divided by 10. This means that
the `tickcb` callback must return a string having an additional significant
digit. If this is not done, consecutive legends will have the same value.

###### [Jump to Contents](./README.md#contents)

# 6. Control Classes

These classes provide touch-sensitive objects capable of both the display and
entry of data. If the user moves the control, its value will change and an
optional callback will be executed. If another control's callback or a
coroutine alters a control's value, its appearance will change accordingly.

## 6.1 Class Button

This emulates a pushbutton, with a callback being executed each time the button
is pressed. Buttons may be any one of three shapes: `CIRCLE`, `RECTANGLE`
or `CLIPPED_RECT`.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Mandatory keyword only argument:
 * `font` Font for button text

Optional keyword only arguments:
 * `shape` CIRCLE, RECTANGLE or CLIPPED_RECT. Default RECTANGLE.
 * `height` Height of the bounding box. Default 20 pixels.
 * `width` Width of the bounding box. Default 50 pixels.
 * `fill` Boolean. If `True` the button will be filled with the current
 `fgcolor`.
 * `fgcolor` Color of foreground (the control itself). Defaults to system
 color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `fontcolor` Text color. Defaults to system text color.
 * `litcolor` If provided the button will display this color for one second
 after being pressed.
 * `text` Shown in centre of button. Default: an empty string.
 * `callback` Callback function which runs when button is pressed.
 * `args` A list/tuple of arguments for the above callback. Default `[]`.
 * `onrelease` Default `True`. If `True` the callback will occur when the
 button is released otherwise it will occur when pressed. See
 [Application design note](./README.md#10-application-design-note) for the
 reason for this default.
 * `lp_callback` Callback to be used if button is to respond to a long press.
 Default `None`.
 * `lp_args` A list/tuple of arguments for above callback. Default `[]`.

Method:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.

Class variables:
 * `lit_time` Period in seconds the `litcolor` is displayed. Default 1.
 * `long_press_time` Press duration for a long press. Default 1 second.

###### [Jump to Contents](./README.md#contents)

## 6.2 Class ButtonList emulate a button with multiple states

A `ButtonList` groups a number of buttons together to implement a button
which changes state each time it is pressed. For example it might toggle
between a green Start button and a red Stop button. The buttons are defined and
added in turn to the `ButtonList` object. Typically they will be the same
size, shape and location but will differ in color and/or text. At any time just
one of the buttons will be visible, initially the first to be added to the
object.

Buttons in a `ButtonList` should not have callbacks. The `ButtonList` has
its own user supplied callback which will run each time the object is pressed.
However each button can have its own list of `args`. Callback arguments
comprise the currently visible button followed by its arguments.

Constructor argument:
 * `callback` The callback function. Default does nothing.

Methods:
 * `add_button` Adds a button to the `ButtonList`. Arguments: as per the
 `Button` constructor.
 Returns the button object.
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Optional argument: a button in the set. If supplied and the button
 is not active the currency changes to the supplied button and its callback is
 run. Always returns the active button.

Typical usage is as follows:
``python
def callback(button, arg):
    print(arg)

table = [
     {'fgcolor' : GREEN, 'shape' : CLIPPED_RECT, 'text' : 'Start', 'args' : ['Live']},
     {'fgcolor' : RED, 'shape' : CLIPPED_RECT, 'text' : 'Stop', 'args' : ['Die']},
]
bl = ButtonList(callback)
for t in table: # Buttons overlay each other at same location
    bl.add_button((10, 10), font = font14, fontcolor = BLACK, **t)
``

###### [Jump to Contents](./README.md#contents)

## 6.3 Class RadioButtons

These comprise a set of buttons at different locations. When a button is
pressed, it becomes highlighted and remains so until another button is pressed.
A callback runs each time the current button is changed.

Constructor positional arguments:
 * `highlight` Color to use for the highlighted button. Mandatory.
 * `callback` Callback when a new button is pressed. Default does nothing.
 * `selected` Index of initial button to be highlighted. Default 0.

Methods:
 * `add_button` Adds a button. Arguments: as per the `Button` constructor.
 Returns the Button instance.
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Optional argument: a button in the set. If supplied, and the
 button is not currently active, the currency changes to the supplied button
 and its callback is run. Always returns the currently active button.

Typical usage:
```python
def callback(button, arg):
    print(arg)

table = [
    {'text' : '1', 'args' : ['1']},
    {'text' : '2', 'args' : ['2']},
    {'text' : '3', 'args' : ['3']},
    {'text' : '4', 'args' : ['4']},
]
x = 0
rb = RadioButtons(callback, BLUE) # color of selected button
for t in table:
    rb.add_button((x, 180), font = font14, fontcolor = WHITE,
                    fgcolor = LIGHTBLUE, height = 40, **t)
    x += 60 # Horizontal row of buttons
```

###### [Jump to Contents](./README.md#contents)

## 6.4 Class Slider

These emulate linear potentiometers. Vertical `Slider` and horizontal
`HorizSlider` variants are available. These are constructed and used
similarly. The short forms (v) or (h) are used below to identify these
variants. See the note above on callbacks.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Optional keyword only arguments:
 * `font` Font to use for any legends. Default `None`: no legends will be
 drawn.
 * `height` Dimension of the bounding box. Default 120 pixels (v), 20 (h).
 * `width` Dimension of the bounding box. Default 20 pixels (v), 120 (h).
 * `divisions` Number of graduations on the scale. Default 10.
 * `legends` A tuple of strings to display near the slider. These `Label`
 instances will be  distributed evenly along its length, starting at the bottom
 (v) or left (h).
 * `fgcolor` Color of foreground (the control itself). Defaults to system
 color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `fontcolor` Text color. Defaults to system text color.
 * `slidecolor` Color for the slider. Defaults to the foreground color.
 * `border` Width of border. Default `None`: no border will be drawn. If a
 value (typically 2) is provided, a border line will be drawn around the
 control.
 * `cb_end` Callback function which will run when the user stops touching the
 control.
 * `cbe_args` A list/tuple of arguments for above callback. Default `[]`.
 * `cb_move` Callback function which will run when the user moves the slider
 or the value is changed programmatically.
 * `cbm_args` A list/tuple of arguments for above callback. Default `[]`.
 * `value` The initial value. Default 0.0: slider will be at the bottom (v),
 left (h).

Methods:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Optional arguments `val` (default `None`). If supplied the
 slider moves to reflect the new value and the `cb_move` callback is
 triggered. The method constrains the range to 0.0 to 1.0. Always returns the
 control's value.
 * `color` Mandatory arg `color` The control is rendered in the selected
 color. This supports dynamic color changes  

###### [Jump to Contents](./README.md#contents)

## 6.5 Class Knob

This emulates a rotary control capable of being rotated through a predefined
arc.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Optional keyword only arguments:
 * `height` Dimension of the square bounding box. Default 50 pixels.
 * `arc` Amount of movement available. Default 2*PI radians (360 degrees).
 * `ticks` Number of graduations around the dial. Default 9.
 * `fgcolor` Color of foreground (the control itself). Defaults to system
 color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `color` Fill color for the control knob. Default: no fill.
 * `border` Width of border. Default `None`: no border will be drawn. If a
 value (typically 2) is provided, a border line will be drawn around the
 control.
 * `cb_end` Callback function which will run when the user stops touching the
 control.
 * `cbe_args` A list/tuple of arguments for above callback. Default `[]`.
 * `cb_move` Callback function which will run when the user moves the knob or
 the value is changed.
 * `cbm_args` A list/tuple of arguments for above callback. Default `[]`.
 * `value` Initial value. Default 0.0: knob will be at its most
 counter-clockwise position.

Methods:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Optional argument `val`. If set, adjusts the pointer to
 correspond to the new value. The move callback will run. The method constrains
 the range to 0.0 to 1.0. Always returns the control's value.

###### [Jump to Contents](./README.md#contents)

## 6.6 Class Checkbox

This provides for boolean data entry and display. In the `True` state the
control can show an 'X' or a filled block of any color.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Optional keyword only arguments:
 * `height` Dimension of the square bounding box. Default 20 pixels.
 * `fillcolor` Fill color of checkbox when `True`. Default `None`: an 'X'
 will be drawn.
 * `fgcolor` Color of foreground (the control itself). Defaults to system
 color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `border` Width of border. Default `None`: no border will be drawn. If a
 value (typically 2) is provided, a border line will be drawn around the
 control.
 * `callback` Callback function which will run when the value changes.
 * `args` A list/tuple of arguments for above callback. Default `[]`.
 * `value` Initial value. Default `False`.

Methods:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Optional boolean argument `val`. If the provided value does not
 correspond to the control's current value, updates it; the checkbox is
 re-drawn and the callback executed. Always returns the control's value.

###### [Jump to Contents](./README.md#contents)


## 6.7 Class Listbox

The height of a listbox is determined by the number of entries in it and the
font in use. Scrolling is not supported.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Mandatory keyword only arguments:
 * `font`
 * `elements` A list or tuple of strings to display. Must have at least one
 entry.

Optional keyword only arguments:
 * `width` Control width in pixels, default 80.
 * `value` Index of currently selected list item. Default 0.
 * `border` Space between border and contents. Default 2 pixels. If `None`
 no border will be drawn.
 * `fgcolor` Color of foreground (the control itself). Defaults to system
 color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `fontcolor` Text color. Defaults to system text color.
 * `select_color` Background color for selected item in list. Default
 `LIGHTBLUE`.
 * `callback` Callback function which runs when a list entry is picked.
 * `args` A list/tuple of arguments for above callback. Default `[]`.

Methods:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Argument `val` default `None`. If the argument is provided
 which is a valid index into the list that entry becomes current and the
 callback is executed. Always returns the index of the currently active entry.
 * `textvalue` Argument `text` a string default `None`. If the argument
 is provided and is in the control's list, that item becomes current. Returns
 the current string, unless the arg was provided but did not correspond to any
 list item. In this event the control's state is not changed and `None` is
 returned.

The callback is triggered whenever a listbox item is pressed, even if that item
is already currently selected.

###### [Jump to Contents](./README.md#contents)

## 6.8 Class Dropdown

A dropdown list. The list, when active, is drawn below the control. The height
of the control is determined by the height of the font in use. The height of
the list is determined by the number of entries in it and the font in use.
Scrolling is not supported.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Mandatory keyword only arguments:
 * `font`
 * `elements` A list or tuple of strings to display. Must have at least one
 entry.

Optional keyword only arguments:
 * `width` Control width in pixels, default 100.
 * `value` Index of currently selected list item. Default 0.
 * `fgcolor` Color of foreground (the control itself). Defaults to system
 color.
 * `bgcolor` Background color of object. Defaults to system background.
 * `fontcolor` Text color. Defaults to system text color.
 * `select_color` Background color for selected item in list. Default
 `LIGHTBLUE`.
 * `callback` Callback function which runs when a list entry is picked.
 * `args` A list/tuple of arguments for above callback. Default `[]`.

Methods:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it, showing it in its new state.
 * `value` Argument `val` default `None`. If the argument is provided
 which is a valid index into the list that entry becomes current and the
 callback is executed. Always returns the index of the currently active entry.
 * `textvalue` Argument `text` a string default `None`. If the argument
 is provided and is in the control's list, that item becomes current. Returns
 the current string, unless the arg was provided but did not correspond to any
 list item. In this event the control's state is not changed and `None` is
 returned.

The callback is triggered if an item on the dropdown list is touched and that
item is not currently selected (i.e. when a change occurs).

###### [Jump to Contents](./README.md#contents)

## 6.9 Class Pad

This rectangular touchable control is invisible. It can be used to enable
display class instances to respond to touch, or to create other touch sensitive
regions.

Constructor mandatory positional argument:
 1. `location` 2-tuple defining position.

Optional keyword only arguments:
 * `height=20` Dimensions.
 * `width=50`
 * `onrelease=True` If `True` the callback will occur when the pad is released
 otherwise it will occur when pressed. See
 [Application design note](./README.md#10-application-design-note) for the
 reason for this default.
 * `callback=None` Callback function which runs when button is pressed.
 * `args=[]` A list/tuple of arguments for the above callback.
 * `lp_callback=None` Callback to be used if button is to respond to a long
 press.
 * `lp_args=[]` A list/tuple of arguments for above callback.

Method:
 * `greyed_out` Optional boolean argument `val` default `None`. If
 `None` returns the current 'greyed out' status of the control. Otherwise
 enables or disables it - there is no visible effect.

###### [Jump to Contents](./README.md#contents)

## 6.10 Class Textbox

Displays multiple lines of text in a field of fixed dimensions. Text may be
clipped to the width of the control or may be word-wrapped. If the number of
lines of text exceeds the height available, scrolling will occur. Access to
text that has scrolled out of view may be achieved by touching the control or
by calling a method.

Works with fixed and variable pitch fonts. Tab characters are supported for
Python fonts (not for internal fonts): see [Note on tabs](./README.md#6101-note-on-tabs).
```python
from gui.widgets.textbox import Textbox
```

Constructor mandatory positional arguments:
 1. `location` 2-tuple defining position.
 2. `width` Width of the object in pixels.
 3. `nlines` Number of lines of text to display. The object's height is
 determined from the height of the font:  
 `height in pixels = nlines*font_height + 2*border`
 4. `font` Font to use. The internal font `IFont(3)` renders faster than the
 Python fonts.

Keyword only arguments:
 * `border=2` Border width in pixels - typically 2. If `None`, no border will
 be drawn.
 * `fgcolor=None` Color of border. Defaults to system color.
 * `bgcolor=None` Background color of object. Defaults to system background.
 * `fontcolor=None` Text color. Defaults to system text color.
 * `clip=True` By default lines too long to display are right clipped. If
 `False` is passed, word-wrap is attempted. If the line contains no spaces
 it will be wrapped at the right edge of the window.
 * `repeat=True` Controls the behaviour of touch-based scrolling. By default
 a long press causes repeated scrolling. `False` requires a discrete press for
 each line movement.
 * `tab=32` Tab space in pixels: see [Note on tabs](./README.md#6101-note-on-tabs).

Methods:
 * `append` Args `s, ntrim=None, line=None` Append the string `s` to the
 display and scroll up as required to show it. By default only the number of
 lines which will fit on screen are retained. If an integer `ntrim=N` is
 passed, only the last N lines are retained; `ntrim` may be greater than can be
 shown in the control, hidden lines being accessed by scrolling.  
 If an integer (typically 0) is passed in `line` the display will scroll to
 show that line.
 * `scroll` Arg `n` Number of lines to scroll. A negative number scrolls up. If
 scrolling would achieve nothing because there are no extra lines to display,
 nothing will happen. Returns `True` if scrolling occurred, otherwise `False`.
 * `value` No args. Returns the number of lines of text stored in the widget.
 * `clear` No args. Clears all lines from the widget and refreshes the display.
 * `goto` Arg `line=None` Fast scroll to a line. By default shows the end of
 the text. 0 shows the start.

Fast updates:  
Rendering text to the screen is relatively slow. To send a large amount of text
the fastest way is to perform a single `append`. Text may contain newline
(`'\n'`) characters as required. In that way rendering occurs once only.

`ntrim`__
If text is regularly appended to a `Textbox` its buffer grows, using RAM. The
value of `ntrim` sets a limit to the number of lines which are retained, with
the oldest (topmost) being discarded as required.

### 6.10.1 Note on tabs

The purpose of tab characters is to align columns of text when using variable
pitch fonts. With fixed pitch fonts (such as internal fonts) they serve no
purpose which cannot be achieved by the Python `format` command. Hence they are
unsupported for internal fonts whose rendering prioritises speed.

###### [Jump to Contents](./README.md#contents)

# 7. Dialog Boxes

In general `Screen` objects occupy the entire physical display. The principal
exception to this is modal dialog boxes which are rendered in a window which
accepts all touch events until it is closed. Dialog boxes are created by
instantiating an `Aperture` which is a `Screen` superclass. In effect this
is a window, but a 'micro' implementation lacking chrome beyond a simple border
and occupying a fixed location on the screen.

In use the user program creates a class subclassed from `Aperture`. This is
populated in the same way as per `Screen` subclasses. The class name can then
be passed to `Screen.change` to invoke the dialog box. The GUI provides a
simple way to build dialog boxes based on a small set of pushbuttons such as
'Yes/No/Cancel' in the form of the `DialogBox` class.

A convenience method `locn` is provided to assist in populating dialog boxes.
Given coordinates relative to the dialog box, it provides an absolute
`location` 2-tuple suitable as a constructor argument for `control` or
`display` classes. See `ldb.py` for example usage.

###### [Jump to Contents](./README.md#contents)

## 7.1 Class Aperture

Provides a window for objects in a modal dialog box.

Constructor mandatory positional args:  
 1. `location` 2-tuple defining the window position.
 2. `height` Dimensions in pixels.
 3. `width`

Optional keyword only args:  
 * `draw_border` Boolean, default `True`. If set a single pixel window
 border will be drawn.
 * `bgcolor`  Background color of window. Defaults to system background.
 * `fgcolor` Color of border. Defaults to system foreground.

Instance variables:  
 * `location` 2-tuple defining the window position.
 * `height` Dimensions in pixels.
 * `width`

Method:
 * `locn` Args: x, y. Returns an absolute location 2-tuple given a pair of
 coordinates relative to the dialog box.

Class method:  
 * `value` Optional arg `val` default `None`. Provides a mechanism for
 returning the outcome of a dialog box which can be queried by the calling
 object. If the arg is provided, the value is set. The arg may be any Python
 object. Returns the value of the `Aperture` class. The calling `Screen`
 can query this by implementing an `on_open` method which calls
 `Aperture.value()` (see `ldb.py`).

###### [Jump to Contents](./README.md#contents)

## 7.2 Class DialogBox

Eases building a dialog box subset based on a row of pushbuttons. Any button
press will close the dialog. The caller can determine which button was pressed.
The size of the buttons and the width of the dialog box are calculated from the
strings assigned to the buttons. This ensures that buttons are evenly spaced
and identically sized.

Constructor mandatory positional args:
 1. `font` The font for buttons and label.
 
Optional keyword only args:  
 * `elements` A list or tuple of 2-tuples. Each defines the text and color of
 a pushbutton, e.g. `(('Yes', RED), ('No', GREEN))`.
 * `location` 2-tuple defining the dialog box location. Default (20, 20).
 * `label` Text for an optional label displayed in the centre of the dialog
 box. Default `None`.
 * `bgcolor` Background color of window. Default `DARKGREEN`.
 * `buttonwidth` Minimum width of buttons. Default 25. In general button
 dimensions are calculated from the size of the strings in `elements`.  
 * `closebutton` Boolean. If set, a `close` button will be displayed at the
 top RH corner of the dialog box.

Pressing any button closes the dialog and sets the `Aperture` value to the
text of the button pressed or 'Close' in the case of the `close` button.

###### [Jump to Contents](./README.md#contents)

# 8. Fonts

The LCD160CR contains internal fixed pitch fonts. These may be used as an
alternative to external fonts converted from `ttf` or `otf` files and are
likely to result in better text rendering at small sizes. External fonts enable
arbitrary fonts to be used including ones with variable pitch.

## 8.1 External fonts

Fonts may be created using the `font_to_py.py` utility documented
[here](https://github.com/peterhinch/micropython-font-to-py.git). The `-x`
argument should be employed. The resultant Python file may be imported and
the module passed to the constructor of GUI objects. These files may be
frozen as bytecode to radically reduce RAM usage.

The `LCD160CR_G` constructor has an optional constructor keyword argument
`bufsize`. This defines the size of an internal character buffer, required if
using external fonts. If an application's largest external font has dimensions
`h*w` pixels, the buffer must be at least `h*w*2` bytes in size. The
default of 1058 bytes provides for external fonts up to 23 by 23 pixels.

A `UguiException` will be raised if an application attempts to use a font too
large for the buffer.

###### [Jump to Contents](./README.md#contents)

## 8.2 Internal fonts Class IFont

To use internal fonts an `IFont` is instantiated. The instance is then passed
to GUI constructors in the same way as for external fonts. See test program
`ldb_if.py` for an example.

Constructor mandatory positional arg:
 * `family` 0 to 3. Determines the size of the font.

Optional args:
 * `scale` Pixels are drawn as a square with side length equal to scale + 1.
 The value can be between 0 and 63 (default 0).
 * `bold_h` Controls the number of pixels to overdraw each character pixel in
 the horizontal direction making a bold effect. Value 0 to 3 (default 0).
 * `bold_v` Controls the number of pixels to overdraw each character pixel in
 the vertical direction making a bold effect. Value 0 to 3 (default 0).

###### [Jump to Contents](./README.md#contents)

# 9. Issues

There was a problem with detection of long button presses (MicroPython issue
#2879). This was resolved in early 2017 by an upgrade to the LCD160CR firmware.
If running an old display device you may need to request an upgrade.

# 10. Application design note

There is an issue in a touch application where a control causes a new screen
to overlay the current screen, or closes a screen to reveal the one below.
Consider a `X` screen close button at the top right hand corner of each screen.
If touched, the screen closes revealing the one below with its `X` button: the
touch causes this immediately to be activated closing that screen too.

For this reason the [Button class](./README.md#64-class-button) defaults to
running the callback on release. While this fixes the problem of close buttons,
it can introduce problems where buttons open screens: if multiple buttons are
pressed at once, unexpected screen changes can occur. Either set such buttons
to run the callback on press or use a control such as a listbox.

The general point, where screens change, is to consider how continuing touch
will affect the new screen.

# 11. ESP32

The official display may be connected to non-Pyboard targets via I2C and SPI
interfaces. Both interfaces are required by the GUI. The display has an AP2210
LDO voltage regulator so it may be powered from 5V or 3.3V. Connections may be
made via the downward facing pins or the black connector at the end of the PCB.
In my testing the SPI connections on that connector
[do not work](https://github.com/micropython/micropython/issues/6663), however
the power and I2C connections were OK.

The downward facing pins are as follows. The table is arranged such that the
black connector is at the top. The view is looking at the display surface.

Pin names are those on a mating Pyboard 1.x. Only signals with an entry in the
`Link` column require connection to the target.

| Pin | Signal  | Link | Signal | Link | Pin |
|:---:|:-------:|:----:|:------:|:----:|:---:|
| Y1  | UART Rx |      | Vin    | 5V   | Vin |
| Y2  | UART Tx |      | NC     |      | 3V3 |
| Y3  | LCD CS1 |      | Gnd    | Gnd  | Gnd |
| Y4  | PWR     | PWR  | Rst    |      | Rst |
| Y5  | SS\     |      | LCD BL |      | Y12 |
| Y6  | SCK     | SPI  | T-IRQ  |      | Y11 |
| Y7  | MISO    |      | SDA    | I2C  | Y10 |
| Y8  | MOSI    | SPI  | SCL    | I2C  | Y9  |

The `PWR` signal enables power to the display by turning on the internal LDO
3.3V regulator. It should be assigned to an arbitrary I/O pin. In testing I
found it necessary to assert `PWR` and wait before instantiating the display
(see code below). The display board has no I2C pullups. If the target lacks
them, pullups to 3.3V on `SDA` and `SCL` are essential. Values are uncritical:
1.5KΩ to 4.7KΩ are typical.

Note on the SPI interface: the LCD160CR hardware does not implement `MISO`: SPI
is from target to display only. Nor does it
[implement `SS\`](https://github.com/micropython/micropython/issues/6663) (also
known as `CS\`) which means it requires exclusive access to the SPI bus.

The ESP32 allows arbitrary pin assignments, but
[the docs](http://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus)
recommend hardware SPI on default pins for performance and reliability. Owing
to the limited performance of I2C I would expect any pin configuration to work
with this interface but I haven't tested this.

I tested with this wiring. The ESP column represents ESP32 GPIO numbers, the
Pin column represents the name of the downward facing pin on the display. This
is the Pyboard pin it would mate with, not the names on the silkscreen which
refer to edge connectors. Once again this is the view looking down on the
display with the 10-way black edge connector at the top.

| Pin | Signal | ESP  | Signal | ESP  | Pin |
|:---:|:------:|:----:|:------:|:----:|:---:|
| Y1  |        |      | Vin    | 5V   | Vin |
| Y2  |        |      |        |      |     |
| Y3  |        |      | Gnd    | Gnd  | Gnd |
| Y4  | PWR    | 25   |        |      | Rst |
| Y5  |        |      |        |      | Y12 |
| Y6  | SCK    | 14   |        |      | Y11 |
| Y7  |        |      | SDA    | 19   | Y10 |
| Y8  | MOSI   | 13   | SCL    | 18   | Y9  |

This code works on the reference board wired as above:
```python
from gui.core import lcd160cr
from gui.core.lcd160_gui import Screen, LCD160CR_G
from gui.widgets.label import Label
import font10

from time import sleep_ms
from machine import Pin, I2C, SPI

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font10, value = 'Hello world')

def main():
    pwr = Pin(25, Pin.OUT)
    pwr(1)
    sleep_ms(100)  # Ensure device is ready
    # Hardware SPI on native pins for performance
    spi = SPI(1, 10_000_000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    i2c = I2C(0, freq=1_000_000)  # scl=Pin(18), sda=Pin(19)
    lcd = LCD160CR_G(pwr=pwr, spi=spi, i2c=i2c)  # Set connection
    lcd.set_orient(lcd160cr.LANDSCAPE)  # and orientation
    Screen.setup(lcd)
    Screen.change(BaseScreen)

main()
```
To install the library on ESP32 the file `lcd_local_esp.py` should be copied to
`/pyboard/lcd_local.py` after making any edits to support your physical
connection and maximum font size.

The supplied [framebuf_utils.mpy](./README.md#15-a-performance-boost) will
produce a harmless warning message because the supplied example is compiled for
STM architecture. To enable fast text rendering on ESP32 it is necessary to
recompile `framebuf_utils.mpy` for `xtensawin`. This is discussed
[here](https://github.com/peterhinch/micropython-font-to-py/blob/master/writer/WRITER.md#224-a-performance-boost).

When instantiating I2C and SPI buses on default pins, the I2C constructor does
not require the pins to be explicitly specified. The SPI constructor does. The
docs don't explicitly state this, but the provided code examples illustrate it.

### Debug notes

If changing the pins or migrating to a different target the following errors
can occur.
 * ENOENT or timeout exception: I2C problem. Check wiring, pullups and pwr
 state.
 * Blank display: check power connections and the pwr pin.
 * The GUI works but lacks text on buttons. Meters and sliders show
 corruption: this is an SPI problem.
