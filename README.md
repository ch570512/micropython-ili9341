# micropython-ili9341
<a href="https://www.buymeacoffee.com/ch570512" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 150px !important;"></a>

This MicroPython class enables the use of (proportional) Adafruit_GFX library fonts with rdagger's [micropython-ili9341](https://github.com/rdagger/micropython-ili9341) display driver.
Simply replace `xglcd_font.py` with `gfx_font.py` in your project — no other changes are required.
All existing functionality of `ili9341.py` remains fully compatible.

> 📖 Full API references (every class, method and function) are available in `API_xxx.md`.

```python
from ili9341 import Display, color565
from gfx_font import GfxFont

font = GfxFont("FreeSansBold24pt7b.h")

text = "Hello world!"
text_w = font.measure_text(text)
x = (320 - text_w) // 2
y = (240 - font.y_advance) // 2
display.draw_text(x, y, text, font, color565(255, 255, 255), color565(255, 0, 0))
```

A simple `print()` function is included that writes to the display like to a console:

```python
def print(
        self, text, color=0xFFFF, background=0, font=None, spacing=0, x=None, y=None,
        scale=1, wrap=True
    ):
        """Print text at an internal cursor, console style.

        The cursor advances after every printed character, so the next call
        to print() continues at the last position. A carriage return (\r)
        or line feed (\n) moves the cursor to the start of the next line.
        Text that would pass the right edge of the display wraps to the
        next line.

        Args:
            text (str): Text to print.
            color (int): RGB565 color value (default: white).
            background (int): RGB565 background color (default: black).
            font (optional): Font object. If None the built-in 8x8 font
                is used.
            spacing (int): Extra pixels between letters (default: 0, only
                used with a custom font).
            x (int|None): Optional start column, overrides the cursor.
            y (int|None): Optional start row, overrides the cursor.
            scale (int): Font scale factor (default: 1, allowed: 1 or 2).
            wrap (bool): Wrap at the right edge (default: True). When False,
                text is clipped at the display edge instead.
        """
```

Set the display rotation at runtime:

```python
def set_rotation(self, rotation, mirror=False):
    """Change display rotation at runtime (re-sends the MADCTL command).
    Args:
        rotation (Optional int): Rotation must be 0 default, 90. 180 or 270
        mirror (Optional bool): Mirror display (default False)
    """
```

For more information on the original library go to https://github.com/rdagger/micropython-ili9341

Copyright © 2026 [ch570512](https://github.com/ch570512)
