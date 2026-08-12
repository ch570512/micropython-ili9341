# ILI9341 Driver API Reference

Complete reference for `ili9341.py`, a MicroPython/CircuitPython driver for the
ILI9341 320×240 TFT display (16-bit 5-6-5 RGB color).

> **Note:** All coordinates are zero based.

---

## Module-level functions

### `color565(r, g, b)`

Converts separate red, green and blue values into a single 16-bit RGB565 color value.

| Arg | Type | Description |
|-----|------|-------------|
| `r` | int | Red value (0–255) |
| `g` | int | Green value (0–255) |
| `b` | int | Blue value (0–255) |

**Returns:** `int` — packed RGB565 value (e.g. `color565(255, 255, 255)` = white).

```python
from ili9341 import Display, color565
white = color565(255, 255, 255)
```

---

## Class `Display`

Serial interface for the ILI9341 display. All drawing primitives are methods on
this class.

### `__init__(spi, cs, dc, rst, width=240, height=320, rotation=0, mirror=False, bgr=True, gamma=True, x_offset=0, y_offset=0)`

Initializes the display, resets it and sends the full set of ILI9341 init commands.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `spi` | `SPI` | — | SPI interface for the display |
| `cs` | `Pin` | — | Chip select pin |
| `dc` | `Pin` | — | Data/Command pin |
| `rst` | `Pin` | — | Reset pin |
| `width` | int | `240` | Screen width in pixels |
| `height` | int | `320` | Screen height in pixels |
| `rotation` | int | `0` | Rotation, must be `0`, `90`, `180` or `270` |
| `mirror` | bool | `False` | Mirror the display |
| `bgr` | bool | `True` | Swap red and blue channels |
| `gamma` | bool | `True` | Use custom gamma correction values |
| `x_offset` | int | `0` | X-axis origin offset |
| `y_offset` | int | `0` | Y-axis origin offset |

Raises `ValueError` if `(mirror, rotation)` is not a valid combination.

**Note:** on MicroPython the SPI pins are passed via the `spi` object; the `Pin`
objects are initialized internally for `cs`, `dc` and `rst`.

```python
from machine import Pin, SPI
from ili9341 import Display

spi = SPI(1, baudrate=40_000_000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
display = Display(spi, dc=Pin(4), cs=Pin(15), rst=Pin(27), width=320, height=240)
```

---

### Display control

#### `block(x0, y0, x1, y1, data)`

Write a rectangular block of raw pixel data to the display.

| Arg | Type | Description |
|-----|------|-------------|
| `x0` | int | Starting X position |
| `y0` | int | Starting Y position |
| `x1` | int | Ending X position |
| `y1` | int | Ending Y position |
| `data` | bytes | RGB565 pixel data buffer |

Applies `x_offset`/`y_offset` if configured. Low-level building block used by
most drawing methods.

#### `clear(color=0, hlines=8)`

Fill the entire display with a single color.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `color` | int | `0` | RGB565 fill color (default black) |
| `hlines` | int | `8` | Horizontal lines per chunk. Must be a non-zero factor of the height. Smaller values use less RAM; larger values clear faster. |

Also resets the console print cursor to the top-left corner.

```python
display.clear(color565(0, 0, 255))   # blue screen
display.clear()                      # black screen
```

#### `cleanup()`

Clear the screen, turn the display off and deinitialize the SPI bus.

#### `display_off()`

Send the `DISPLAY_OFF` command (screen goes dark, controller stays powered).

#### `display_on()`

Send the `DISPLAY_ON` command (wake the screen after `display_off()`).

#### `invert(enable=True)`

Enable or disable color inversion.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `enable` | bool | `True` | `True` = invert colors, `False` = normal |

#### `set_rotation(rotation, mirror=False)`

Change display rotation at runtime (re-sends the `MADCTL` command).

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `rotation` | int | — | `0`, `90`, `180` or `270` |
| `mirror` | bool | `False` | Mirror display |

Raises `ValueError` on an invalid rotation/mirror combination.

#### `sleep(enable=True)`

Enter or exit sleep mode.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `enable` | bool | `True` | `True` = enter sleep, `False` = exit sleep |

---

### Scrolling

#### `scroll(y)`

Scroll the display vertically.

| Arg | Type | Description |
|-----|------|-------------|
| `y` | int | Number of pixels to scroll |

#### `set_scroll(top, bottom)`

Set the height of the top and bottom scroll margins (the middle region scrolls).

| Arg | Type | Description |
|-----|------|-------------|
| `top` | int | Height of the top margin |
| `bottom` | int | Height of the bottom margin |

---

### Primitives (points, lines, shapes)

#### `draw_pixel(x, y, color)`

Draw a single pixel.

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | X position |
| `y` | int | Y position |
| `color` | int | RGB565 color |

#### `draw_hline(x, y, w, color)`

Draw a horizontal line.

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | Starting X position |
| `y` | int | Y position |
| `w` | int | Line width in pixels |
| `color` | int | RGB565 color |

#### `draw_vline(x, y, h, color)`

Draw a vertical line.

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | X position |
| `y` | int | Starting Y position |
| `h` | int | Line height in pixels |
| `color` | int | RGB565 color |

#### `draw_line(x1, y1, x2, y2, color)`

Draw a line between two points using Bresenham's algorithm.

| Arg | Type | Description |
|-----|------|-------------|
| `x1, y1` | int | Start coordinates |
| `x2, y2` | int | End coordinates |
| `color` | int | RGB565 color |

#### `draw_lines(coords, color)`

Draw multiple connected line segments.

| Arg | Type | Description |
|-----|------|-------------|
| `coords` | list | List of `[x, y]` coordinate pairs |
| `color` | int | RGB565 color |

#### `draw_rectangle(x, y, w, h, color)`

Draw the outline of a rectangle.

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | Starting X position |
| `y` | int | Starting Y position |
| `w` | int | Width |
| `h` | int | Height |
| `color` | int | RGB565 color |

#### `draw_circle(x0, y0, r, color)`

Draw the outline of a circle (Bresenham).

| Arg | Type | Description |
|-----|------|-------------|
| `x0, y0` | int | Center coordinates |
| `r` | int | Radius |
| `color` | int | RGB565 color |

#### `draw_ellipse(x0, y0, a, b, color)`

Draw the outline of an ellipse.

| Arg | Type | Description |
|-----|------|-------------|
| `x0, y0` | int | Center coordinates |
| `a` | int | Semi-major axis (X) |
| `b` | int | Semi-minor axis (Y) |
| `color` | int | RGB565 color |

#### `draw_polygon(sides, x0, y0, r, color, rotate=0)`

Draw a regular n-sided polygon outline.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `sides` | int | — | Number of sides |
| `x0, y0` | int | — | Center coordinates |
| `r` | int | — | Radius |
| `color` | int | — | RGB565 color |
| `rotate` | float | `0` | Rotation in degrees |

---

### Filled shapes

#### `fill_rectangle(x, y, w, h, color)`

Draw a filled rectangle. Auto-selects horizontal or vertical chunking based on
width vs. height for efficiency.

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | Starting X position |
| `y` | int | Starting Y position |
| `w` | int | Width |
| `h` | int | Height |
| `color` | int | RGB565 color |

#### `fill_hrect(x, y, w, h, color)`

Draw a filled rectangle optimized for horizontal drawing (chunked along rows).

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | Starting X position |
| `y` | int | Starting Y position |
| `w` | int | Width |
| `h` | int | Height |
| `color` | int | RGB565 color |

#### `fill_vrect(x, y, w, h, color)`

Draw a filled rectangle optimized for vertical drawing (chunked along columns).

| Arg | Type | Description |
|-----|------|-------------|
| `x` | int | Starting X position |
| `y` | int | Starting Y position |
| `w` | int | Width |
| `h` | int | Height |
| `color` | int | RGB565 color |

#### `fill_circle(x0, y0, r, color)`

Draw a filled circle.

| Arg | Type | Description |
|-----|------|-------------|
| `x0, y0` | int | Center coordinates |
| `r` | int | Radius |
| `color` | int | RGB565 color |

#### `fill_ellipse(x0, y0, a, b, color)`

Draw a filled ellipse.

| Arg | Type | Description |
|-----|------|-------------|
| `x0, y0` | int | Center coordinates |
| `a` | int | Semi-major axis (X) |
| `b` | int | Semi-minor axis (Y) |
| `color` | int | RGB565 color |

#### `fill_polygon(sides, x0, y0, r, color, rotate=0)`

Draw a filled regular n-sided polygon.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `sides` | int | — | Number of sides |
| `x0, y0` | int | — | Center coordinates |
| `r` | int | — | Radius |
| `color` | int | — | RGB565 color |
| `rotate` | float | `0` | Rotation in degrees |

---

### Text

#### `draw_text(x, y, text, font, color, background=0, landscape=False, rotate_180=False, spacing=1)`

Draw a string using a proportional font object (e.g. `GfxFont` / `XglcdFont`).

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `x` | int | — | Starting X position |
| `y` | int | — | Starting Y position |
| `text` | str | — | Text to draw |
| `font` | object | — | Font object with a `get_letter()` method |
| `color` | int | — | RGB565 text color |
| `background` | int | `0` | RGB565 background color |
| `landscape` | bool | `False` | `True` = letters drawn vertically |
| `rotate_180` | bool | `False` | Rotate text by 180° |
| `spacing` | int | `1` | Pixels between letters |

Prints a warning and returns if a letter has invalid dimensions.

#### `draw_text8x8(x, y, text, color, background=0, rotate=0)`

Draw text using MicroPython's built-in 8×8 bitmap font (via `framebuf`).

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `x` | int | — | Starting X position |
| `y` | int | — | Starting Y position |
| `text` | str | — | Text to draw |
| `color` | int | — | RGB565 text color |
| `background` | int | `0` | RGB565 background color |
| `rotate` | int | `0` | `0`, `90`, `180` or `270` |

#### `print(text, color=0xFFFF, background=0, font=None, spacing=1, x=None, y=None)`

Print text at an internal cursor, console style.

The cursor advances after every printed character, so the next call to `print()`
continues at the last position. A carriage return (`\r`) or line feed (`\n`)
moves the cursor to the start of the next line. Text that would pass the right
edge of the display wraps to the next line.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `text` | str | — | Text to print |
| `color` | int | `0xFFFF` | RGB565 text color (white) |
| `background` | int | `0` | RGB565 background color (black) |
| `font` | object | `None` | Font object; `None` uses the built-in 8×8 font |
| `spacing` | int | `1` | Extra pixels between letters (custom font only) |
| `x` | int | `None` | Optional start column, overrides the cursor |
| `y` | int | `None` | Optional start row, overrides the cursor |

```python
display.print("Hello")                 # built-in font at cursor
display.print("World!", x=0, y=10)     # override cursor position
```

---

### Images & sprites

#### `draw_image(path, x=0, y=0, w=320, h=240)`

Draw an image stored on flash. The image must be raw RGB565 data (as written by
this driver). The file is streamed in chunks to limit RAM usage.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `path` | str | — | Path to the raw image file |
| `x` | int | `0` | Image X position |
| `y` | int | `0` | Image Y position |
| `w` | int | `320` | Image width |
| `h` | int | `240` | Image height |

#### `load_sprite(path, w, h)`

Load a sprite (raw RGB565 data) from flash into RAM and return it as bytes.

| Arg | Type | Description |
|-----|------|-------------|
| `path` | str | Path to the sprite file |
| `w` | int | Sprite width |
| `h` | int | Sprite height |

**Returns:** `bytes` — sprite pixel data.

> **Note:** `w × h` cannot exceed 2048 pixels on boards without PSRAM.

#### `draw_sprite(buf, x, y, w, h)`

Draw a sprite from a pixel buffer, optimized for horizontal drawing.

| Arg | Type | Description |
|-----|------|-------------|
| `buf` | bytes | Sprite RGB565 pixel data |
| `x` | int | Sprite X position |
| `y` | int | Sprite Y position |
| `w` | int | Sprite width |
| `h` | int | Sprite height |

---

### Utility

#### `draw_letter(x, y, letter, font, color, background=0, landscape=False, rotate_180=False)`

Draw a single character using a font object. Called internally by `draw_text()`.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `x` | int | — | Starting X position |
| `y` | int | — | Starting Y position |
| `letter` | str | — | Character to draw |
| `font` | object | — | Font object |
| `color` | int | — | RGB565 text color |
| `background` | int | `0` | RGB565 background color |
| `landscape` | bool | `False` | Draw letter vertically |
| `rotate_180` | bool | `False` | Rotate letter by 180° |

**Returns:** `(w, h)` — width and height of the drawn letter (or `(0, 0)` if
off-grid).

#### `is_off_grid(xmin, ymin, xmax, ymax)`

Check whether a bounding box extends past the display boundaries.

| Arg | Type | Description |
|-----|------|-------------|
| `xmin` | int | Minimum X |
| `ymin` | int | Minimum Y |
| `xmax` | int | Maximum X |
| `ymax` | int | Maximum Y |

**Returns:** `bool` — `False` = coordinates OK, `True` = out of bounds (also
prints a diagnostic message).

#### `reset_cpy()` / `reset_mpy()`

Perform a hardware reset (low = init, high = normal). The `cpy` variant is used
on CircuitPython, `mpy` on MicroPython; the correct one is bound automatically
in `__init__`.

---

### Low-level SPI (normally called internally)

#### `write_cmd(command, *args)`

Write an ILI9341 command byte, optionally followed by argument bytes. Bound
automatically to the platform-specific `write_cmd_mpy`/`write_cmd_cpy`.

| Arg | Type | Description |
|-----|------|-------------|
| `command` | int | ILI9341 command code |
| `*args` | int... | Optional data bytes to transmit |

#### `write_data(data)`

Write a raw data payload to the display. Bound automatically to the
platform-specific `write_data_mpy`/`write_data_cpy`.

| Arg | Type | Description |
|-----|------|-------------|
| `data` | bytes | Data to transmit |

#### `write_cmd_mpy(command, *args)`

MicroPython implementation of `write_cmd`. Sets DC low, CS low, writes the
command byte, then transmits any argument bytes as data.

#### `write_cmd_cpy(command, *args)`

CircuitPython implementation of `write_cmd`. Uses `spi.try_lock()` to safely
claim the SPI bus before writing.

#### `write_data_mpy(data)`

MicroPython implementation of `write_data`. Sets DC high, CS low, writes the
payload.

#### `write_data_cpy(data)`

CircuitPython implementation of `write_data`. Uses `spi.try_lock()` around the
write.

---

## Class attributes (command constants)

All ILI9341 register command codes are exposed as class constants, e.g.
`Display.SWRESET`, `Display.MADCTL`, `Display.DISPLAY_ON`, `Display.PIXFMT`.
These are mostly used internally by `__init__` but are available for advanced
use (e.g. issuing raw commands).

```python
display.write_cmd(Display.INVON)   # manually invert colors
```

`MIRROR_ROTATE` is a dict mapping `(mirror, rotation)` tuples to the matching
`MADCTL` value.

---

## Quick start (MicroPython)

```python
from machine import Pin, SPI
from ili9341 import Display, color565
from gfx_font import GfxFont

spi = SPI(1, baudrate=40_000_000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
display = Display(spi, dc=Pin(4), cs=Pin(15), rst=Pin(27), width=320, height=240)

font = GfxFont("FreeSansBold24pt7b.h")
display.draw_text(
    10, 10, "Hello!",
    font, color565(255, 255, 255), color565(255, 0, 0), spacing=1,
)
display.print("Console line 1")
display.print("Console line 2")
```
