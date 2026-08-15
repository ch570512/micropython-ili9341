# XPT2046 Driver API Reference

Complete reference for `xpt2046.py`, a MicroPython/CircuitPython driver for the
XPT2046 resistive touch screen controller, typically paired with an ILI9341 TFT
display.

The controller is a 12-bit ADC. Raw X/Y values are linearly mapped to display
coordinates through the calibration parameters passed to the constructor.

> **Note:** On MicroPython the SPI pins are passed via the `spi` object; only
> `cs` (chip select) and optionally `int_pin` (interrupt) are `Pin` objects.

---

## Class `Touch`

Serial interface for the XPT2046 touch screen controller.

### `__init__(spi, cs, int_pin=None, int_handler=None, width=240, height=320, x_min=100, x_max=1962, y_min=100, y_max=1900)`

Initializes the controller, configures the chip-select pin and, if given, arms
the interrupt pin.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `spi` | `SPI` | — | SPI interface for the controller |
| `cs` | `Pin` | — | Chip select pin |
| `int_pin` | `Pin` | `None` | Touch interrupt pin (falling edge = press) |
| `int_handler` | function | `None` | Callback `fn(x, y)` invoked on a validated touch |
| `width` | int | `240` | Width of the LCD screen |
| `height` | int | `320` | Height of the LCD screen |
| `x_min` | int | `100` | Minimum raw X value (left edge) |
| `x_max` | int | `1962` | Maximum raw X value (right edge) |
| `y_min` | int | `100` | Minimum raw Y value (top edge) |
| `y_max` | int | `1900` | Maximum raw Y value (bottom edge) |

The raw ADC range `x_min…x_max` / `y_min…y_max` is mapped onto `width` ×
`height` display pixels via the calibration multipliers computed in `__init__`.
The defaults are tuned for a typical 2.4″ module; adjust them if the touch point
drifts.

`int_handler` is only used when `int_pin` is provided; it receives already
normalized display coordinates.

```python
from machine import Pin, SPI
from xpt2046 import Touch

spi2 = SPI(2, baudrate=1_000_000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
touch = Touch(spi2, cs=Pin(5), int_pin=Pin(0), int_handler=on_touch)
```

---

### Touch reading

#### `get_touch()`

Poll the controller until a stable touch is detected (or a 2 s timeout).

Collects up to 5 samples, 50 ms apart. Once 5 samples have been gathered it
computes their mean and deviation; if the deviation is ≤ 50 the mean is
normalized to display coordinates and returned. An invalid sample (e.g. finger
lifted) resets the sample buffer.

**Returns:** `(x, y)` — normalized display coordinates, or `None` on timeout /
no touch.

```python
pos = touch.get_touch()
if pos is not None:
    x, y = pos
    print("touched at", x, y)
```

#### `int_press(pin)`

Interrupt service routine bound to `int_pin` in `__init__` (falling + rising
edges). On a falling edge (press) it reads a raw sample, normalizes it and, if
valid, calls `int_handler(x, y)`. Debounce delays of 0.1 s are applied on both
edges and an `int_locked` flag prevents re-entry while a press is active.

Normally you do not call this directly — pass your callback via `int_handler=`
in the constructor instead.

| Arg | Type | Description |
|-----|------|-------------|
| `pin` | `Pin` | The interrupt `Pin` object (ignored) |

---

### Calibration & raw access

#### `normalize(x, y)`

Map raw ADC coordinates to display coordinates using the calibration
multipliers computed in `__init__`.

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | Raw X value |
| `y` | int | Raw Y value |

**Returns:** `(x, y)` — display coordinates.

#### `raw_touch()`

Read a single raw X/Y sample from the controller.

**Returns:** `(x, y)` — raw 12-bit ADC values if both fall within the configured
`x_min…x_max` / `y_min…y_max` range, otherwise `None`.

---

### Low-level SPI (normally called internally)

#### `send_command(command)`

Write a command byte to the controller and read back the 12-bit response.

| Arg | Type | Description |
|-----|------|-------------|
| `command` | byte | XPT2046 command code (see class attributes below) |

**Returns:** `int` — 12-bit ADC response.

---

## Class attributes (command constants)

The XPT2046 command codes are exposed as class constants:

| Constant | Value | Purpose |
|----------|-------|---------|
| `GET_X` | `0b11010000` | Read X position |
| `GET_Y` | `0b10010000` | Read Y position |
| `GET_Z1` | `0b10110000` | Read Z1 (pressure) |
| `GET_Z2` | `0b11000000` | Read Z2 (pressure) |
| `GET_TEMP0` | `0b10000000` | Read temperature 0 |
| `GET_TEMP1` | `0b11110000` | Read temperature 1 |
| `GET_BATTERY` | `0b10100000` | Battery monitor |
| `GET_AUX` | `0b11100000` | Auxiliary ADC input |

These are used internally by `send_command()` but are available for advanced
use, e.g. reading pressure for a tap/hold distinction:

```python
z1 = touch.send_command(Touch.GET_Z1)
z2 = touch.send_command(Touch.GET_Z2)
```

---

## Quick start (MicroPython)

```python
from machine import idle, Pin, SPI
from ili9341 import Display, color565
from xpt2046 import Touch

def on_touch(x, y):
    y = (display.height - 1) - y   # flip Y to match display orientation
    display.draw_text8x8(0, 0, "{:3d}, {:3d}".format(x, y),
                         color565(255, 255, 255))

spi1 = SPI(1, baudrate=40_000_000, sck=Pin(14), mosi=Pin(13))
display = Display(spi1, dc=Pin(4), cs=Pin(16), rst=Pin(17))

spi2 = SPI(2, baudrate=1_000_000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
touch = Touch(spi2, cs=Pin(5), int_pin=Pin(0), int_handler=on_touch)

try:
    while True:
        idle()
except KeyboardInterrupt:
    display.cleanup()
```

> **Note:** Depending on the display's rotation/mirror settings you may need to
> flip the X or Y axis (as shown above for Y) to align touches with pixels.
