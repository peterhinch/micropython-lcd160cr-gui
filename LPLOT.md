# lplot module

This provides a rudimentary means of displaying two dimensional Cartesian (xy)
and polar graphs on the official Pyboard LCD160CR display. It is an optional
extension to the MicroPython LCD160CR GUI library: this should be installed,
configured and tested before use.

This was ported from the [SSD1963 library](https://github.com/peterhinch/micropython-tft-gui.git).
The small size of the LCD160CR display places practical limits on what can be
placed onscreen alongside a graph.

 1. [Python files](./LPLOT.md#1-python-files)  
 2. [Concepts](./LPLOT.md#2-concepts)  
  2.1 [Graph classes](./LPLOT.md#21-graph-classes)  
  2.2 [Curve classes](./LPLOT.md#22-curve-classes)  
  2.3 [Coordinates](./LPLOT.md#23-coordinates)  
 3. [Graph classes](./LPLOT.md#3-graph-classes) Detailed descriptions.  
  3.1 [Class CartesianGraph](./LPLOT.md#31-class-cartesiangraph)  
  3.2 [Class PolarGraph](./LPLOT.md#32-class-polargraph)  
 4. [Curve classes](./LPLOT.mp#4-curve-classes)  
  4.1 [Class Curve](./LPLOT.md#41-class-curve)  
   4.1.1 [Scaling](./LPLOT.md#411-scaling)  
  4.2 [Class PolarCurve](./LPLOT.md#42-class-polarcurve)  
   4.2.1 [Scaling](./LPLOT.md#421-scaling)  
  4.3 [class TSequence](./LPLOT.md#43-class-tSequence) Plot reatime Y values
  on the time axis.  

# 1. Python files

 1. lplot.py The plot library
 2. lpt.py Test/demo program.
 3. lptg.py Tests/demos using generators to populate curves.

# 2. Concepts

## 2.1 Graph classes

A user program first instantiates a graph object (`PolarGraph` or
`CartesianGraph`). This creates an empty graph image upon which one or more
curves may be plotted. Graphs are GUI display objects: they do not respond to
touch.

## 2.2 Curve classes

The user program then instantiates one or more curves (`Curve` or
`PolarCurve`) as appropriate to the graph. Curves may be assigned colors to
distinguish them.

A curve is plotted by means of a user defined `populate` callback. This
assigns points to the curve in the order in which they are to be plotted. The
curve will be displayed on the graph as a sequence of straight line segments
between successive points.

## 2.3 Coordinates

Graph objects are sized and positioned in terms of TFT screen pixel
coordinates, with (0, 0) being the top left corner of the display, with x
increasing to the right and y increasing downwards. The coordinate system
within a graph conforms to normal mathematical conventions.

Scaling is provided on Cartesian curves enabling user defined ranges for x and
y values. Points lying outside of the defined range will produce lines which
are clipped at the graph boundary.

Points on polar curves are defined as Python `complex` types and should lie
within the unit circle. Points which are out of range may be plotted beyond the
unit circle but will be clipped to the rectangular graph boundary.

# 3. Graph classes

## 3.1 Class CartesianGraph

Constructor.  
Mandatory positional argument:  
 1. `location` 2-tuple defining position.

Keyword only arguments (all optional):  
 * `height=100` Dimension of the bounding box in pixels.
 * `width=140` Dimension of the bounding box.
 * `fgcolor=WHITE` Color of the axis lines.
 * `bgcolor=None` Background color of graph. Defaults to system background.
 * `border=None` Width of border. Default: no border will be drawn.
 * `gridcolor=LIGHTGREEN` Color of grid.
 * `xdivs=10` Number of divisions (grid lines) on x axis.
 * `ydivs=10` Number of divisions on y axis.
 * `xorigin=5` Location of origin in terms of grid divisions. Default 5.
 * `yorigin=5` As `xorigin`. The default of 5, 5 with 10 grid lines on each
 axis puts the origin at the centre of the graph. Settings of 0, 0 would be
 used to plot positive values only.

Method:
 * `clear` Removes all curves from the graph and re-displays the grid.

## 3.2 Class PolarGraph

Constructor.  
Mandatory positional argument:  
 1. `location` 2-tuple defining position.

Keyword only arguments (all optional):  
 * `height=100` Dimension of the square bounding box in pixels.
 * `fgcolor=WHITE` Color of foreground (the axis lines).
 * `bgcolor=None` Background color of object. Defaults to system background.
 * `border=None` Width of border. Default `None`: no border will be drawn.
 * `gridcolor=LIGHTGREEN` Color of grid. Default LIGHTGREEN.
 * `adivs=3` Number of angle divisions per quadrant.
 * `rdivs=4` Number of radius divisions.

Method:
 * `clear` Removes all curves from the graph and re-displays the grid.

# 4. Curve classes

## 4.1 class Curve

The Cartesian curve constructor takes the following positional arguments:

Mandatory argument:
 1. `graph` The `CartesianGraph` instance.

Optional arguments:  
 2. `populate=None` A callback function to populate the curve. See below.  
 3. `args=[]` List or tuple of arguments for `populate` callback.  
 4. `origin=(0, 0)` 2-tuple containing x and y values for the origin.  
 5. `excursion=(1, 1)` 2-tuple containing scaling values for x and y.  
 6. `color` Default YELLOW.  

Methods:
 * `point` Arguments x, y. Defaults `None`. Adds a point to the curve. If a
 prior point exists a line will be drawn between it and the current point. If a
 point is out of range or if either arg is `None` no line will be drawn.
 Passing no args enables discontinuous curves to be plotted.  
 * `show` No args. This can be used to redraw a curve which has been erased
 by the graph's `clear` method. In practice likely to be used when plotting
 changing data from sensors.  

The `populate` callback may be a function, a bound method, a generator function
or a generator function which is a bound method. If it is a generator function
or method the resultant generator should yield x, y pairs for each point to be
plotted (see `lptg.py` for examples). If it is a function or method it should
repeatedly call the `point` method to plot the curve (or delegate that to a
coroutine).

Functions/methods take one or more positional arguments. The first argument is
always the `Curve` instance. Subsequent arguments are any specified in the
curve constructor argument `args`. A typical `populate` generator function:

```python
    def pcb(curve, func):  # curve arg is provided automatically
        x = -1
        while x < 1.01:
            y = func(x)
            yield x, y
            x += 0.1
    curve = Curve(graph, populate=pcb, args=(lambda x : x**3 + x**2 -x,))
```

Another approach is to have a `populate` function which launches a coroutine to
perform data acquisition:

```python
    def __init__(self):
        graph = CartesianGraph((0, 0), height = 127, width = 127)
        curve = Curve(graph, self.go)

    def go(self, curve):
        loop = asyncio.get_event_loop()
        loop.create_task(self.acquire(curve))

    async def acquire(self, curve):
        x = -1
        while x < 1.01:
            y = max(1 - x * x, 0)
            curve.point(x, y ** 0.5)  # Plot in realtime
            x += 0.05
            await asyncio.sleep_ms(100)
```

### 4.1.1 Scaling

To plot x values from 1000 to 4000 we would set the `origin` x value to 1000 and the `excursion`
x value to 3000. The `excursion` values scale the plotted values to fit the corresponding axis.

## 4.2 class PolarCurve

The constructor takes the following positional arguments:

Mandatory argument:
 1. `graph` The `PolarGraph` instance.

Optional arguments:  
 2. `populate=None` A callback function to populate the curve. See below.  
 3. `args=[]` List or tuple of arguments for `populate` callback.  
 4. `color=YELLOW`  

Methods:
 * `point` Argument z, default `None`. Normally a `complex`. Adds a point
 to the curve. If a prior point exists a line will be drawn between it and the
 current point. If the arg is `None` or lies outside the unit circle no line
 will be drawn. Passing no args enables discontinuous curves to be plotted.
 * `show` No args. This can be used to redraw a curve which has been erased by the graph's
 `clear` method. In practice likely to be used when plotting changing data from sensors.

The `populate` callback may be a function, a bound method, a generator function
or a generator function which is a bound method. If it is a generator function
or method the resultant generator should yield complex `z` values for each
point to be plotted (see `lptg.py` for examples). If it is a function or method
it should repeatedly call the `point` method to plot the curve (or delegate
that to a coroutine).

Functions/methods take one or more positional arguments. The first argument is
always the `Curve` instance. Subsequent arguments are any specified in the
curve constructor argument `args`. Example:

```python
    def populate(self, curve):
        def f(theta):
            return rect(sin(3 * theta), theta) # complex
        nmax = 150
        for n in range(nmax + 1):
            theta = 2 * pi * n / nmax
            yield f(theta)
```

### 4.2.1 Scaling

Complex points should lie within the unit circle to be drawn within the grid.

## 4.3 class TSequence

A common task is the acquisition and plotting of real time data against time,
such as hourly temperature and air pressure readings. This class facilitates
this. Time is on the x-axis with the most recent data on the right. Older
points are plotted to the left until they reach the left hand edge when they
are discarded. This is akin to old fashioned pen plotters where the pen was at
the rightmost edge (corresponding to time now) with old values scrolling to the
left with the time axis in the conventional direction.

When a point is drawn the graticule is cleared and re-drawn; the data scrolls
left. This resuts in a momentary flicker. So this class is best suited to
infrequently sampled data such as in meteorological applications.

The user instantiates a graph with the X origin at the right hand side and then
instantiates one or more `TSequence` objects. As each set of data arrives it is
appended to its `TSequence` using the `add` method. See the example below.

The constructor takes the following args:
graph, color, size, yorigin=0, yexc=1
Mandatory arguments:
 1. `graph` The `CartesianGraph` instance.
 2. `color`
 3. `size` Integer. The number of time samples to be plotted. See below.

Optional arguments:  
 4. `yorigin=0` These args provide scaling of Y axis values as per the `Curve`
 class.
 5 `yexc=1`

Method:
 1. `add` Arg `v` the value to be plotted. This should lie between -1 and +1
 unless scaling is applied.

Note that there is little point in setting the `size` argument to a value
greater than the number of X-axis pixels on the graph. It will work but RAM
and execution time will be wasted: the constructor instantiates an array of
floats of this size.

Each time a data set arrives the graph should be cleared, a data value should
be added to each `TSequence` instance, and the display instance should be
refreshed. The following example is taken from demo `lptg.py`.

```python
class Tseq(Screen):
    def __init__(self):
        super().__init__()
        def cancel():
            loop = asyncio.get_event_loop()
            loop.create_task(asyn.Cancellable.cancel_all())
        backbutton(cancel)
        g = CartesianGraph((0, 0), height = 127, width = 127, xorigin = 10)
        tsy = TSequence(g, YELLOW, 50)
        tsr = TSequence(g, RED, 50)
        loop = asyncio.get_event_loop()
        loop.create_task(asyn.Cancellable(self.acquire, g, tsy, tsr)())

    @asyn.cancellable
    async def acquire(self, graph, tsy, tsr):
        t = 0.0
        while True:
            graph.clear()
            tsy.add(0.9 * sin(t))  # Simulate reading data from a sensor.
            tsr.add(0.4 * cos(t))
            await asyncio.sleep_ms(500)
            t += 0.1
```

The cancellation logic enables the plot screen to be cleanly terminated by a
`Button` object. It relies on `asyn.py` from [this repo](https://github.com/peterhinch/micropython-async).
