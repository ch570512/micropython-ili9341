# GFX Font API Reference

Complete reference for `gfx_font.py`, a MicroPython class that loads and renders
**proportional fonts in Adafruit GFX format** — the `.h` header files from the
Adafruit_GFX Arduino library (e.g. `FreeSansBold24pt7b.h`, `TomThumb.h`).

It is a drop-in replacement for `xglcd_font.py` for use with the `ili9341.py`
display driver; no other changes are required.

The constructor parses the three sections of a GFX font file automatically:

- bitmap arrays (`const uint8_t ...[]`),
- the glyph table (`const GFXglyph ...[]`),
- the font header (`const GFXfont ...`) with `first_char`, `last_char` and
  `yAdvance`.

Glyphs are rendered into RGB565 pixel buffers, ready to be passed to
`Display.draw_text()` / `Display.print()`.

---

## Class `GfxFont`

### `__init__(path, scale=1)`

Load and parse a GFX font header file.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `path` | str | — | Path to a GFX `.h` font file |
| `scale` | int | `1` | Integer scale factor for rendering |

After parsing, `letter_count` is set to the number of glyphs in the table and
`_max_ascent` is derived from the glyph y-offsets. The font data is loaded
line-by-line to keep RAM usage low, and `gc.collect()` is called at the end.

```python
from gfx_font import GfxFont

font = GfxFont("FreeSansBold24pt7b.h")        # 1× size
big  = GfxFont("FreeSansBold24pt7b.h", 2)     # 2× size
```

---

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `scale` | int | Render scale factor |
| `bitmaps` | bytearray | Raw glyph bitmap pixel data |
| `glyphs` | `array('i')` | Per-glyph metadata (offset, width, height, xAdvance, xOffset, yOffset) |
| `first_char` | int | Code of the first character in the table (default `0x20` = space) |
| `last_char` | int | Code of the last character in the table (default `0x7E` = `~`) |
| `y_advance` | int | Font line height (`yAdvance`, unscaled) |
| `letter_count` | int | Number of glyphs in the font table |
| `_max_ascent` | int | Maximum ascent (used internally for vertical positioning) |

`y_advance` and `scale` are handy for centering text vertically:

```python
text_h = font.y_advance * font.scale
y = (240 - text_h) // 2
```

---

### `get_letter(letter, color, background=0, landscape=False)`

Render a single character into a bytearray of RGB565 pixel data.

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| `letter` | str | — | Single character to render |
| `color` | int | — | RGB565 text color |
| `background` | int | `0` | RGB565 background color (0 = transparent) |
| `landscape` | bool | `False` | `True` = rotate the glyph 90° (vertical text) |

The returned buffer covers the glyph's **advance box**: width =
`xAdvance × scale`, height = `yAdvance × scale`. The glyph is positioned within
that box using its `xOffset`/`yOffset` and the font's max ascent, so adjacent
letters are spaced correctly.

If `letter` is outside the font's `first_char…last_char` range, a
`Missing char: ...` message is printed and `(b"", 0, 0)` is returned.

**Returns:** `(buf, w, h)` — `buf` is a `bytearray` of RGB565 pixel data, `w`/`h`
are the buffer dimensions (`xAdvance × scale`, `yAdvance × scale`).

```python
buf, w, h = font.get_letter("A", color565(255, 255, 255))
```

> **Note:** `Display.draw_text()` calls `get_letter(letter, color, background)`
> without `landscape`, so glyphs are rendered in portrait orientation there. Use
> `landscape=True` only when rendering directly.

---

### `measure_text(text)`

Measure the pixel width of a text string (using each glyph's `xAdvance ×
scale`).

| Arg | Type | Description |
|-----|------|-------------|
| `text` | str | String to measure |

Characters outside the font's range are skipped (they contribute 0).

**Returns:** `int` — total pixel width of the string.

```python
text = "Hello world!"
text_w = font.measure_text(text)
x = (320 - text_w) // 2          # center horizontally
```

---

## Quick start (MicroPython)

```python
from machine import Pin, SPI
from ili9341 import Display, color565
from gfx_font import GfxFont

spi = SPI(1, baudrate=40_000_000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, dc=Pin(4), cs=Pin(15), rst=Pin(27), width=320, height=240)

font = GfxFont("FreeSansBold24pt7b.h")

text = "Hello world!"
text_w = font.measure_text(text)
x = (320 - text_w) // 2
y = (240 - font.y_advance * font.scale) // 2

display.draw_text(x, y, text, font, color565(255, 255, 255),
                  color565(255, 0, 0), spacing=1)

# Or use the console-style print() with a custom font
display.print("Line 1", font=font, color=color565(255, 255, 0))
```

> **Tip:** All fonts in the `fonts_gfx/` folder are in Adafruit GFX format and
> work directly with `GfxFont`. Custom fonts follow the same three-section
> structure (bitmaps, glyphs, font info).
