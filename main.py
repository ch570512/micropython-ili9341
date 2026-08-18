# Test main.py for micropython-ili9341
# Copyright (C) 2026 by ch570512
# @created 25.07.2026
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from machine import SPI, Pin

from gfx_font import GfxFont
from ili9341 import Display, color565


def _ili9341_init() -> Display:
    display_spi: SPI = SPI(1, baudrate=40_000_000, sck=14, mosi=13, miso=12)
    display: Display = Display(
        display_spi,
        dc=Pin(4),
        cs=Pin(15),
        rst=Pin(27),
        width=320,
        height=240,
        rotation=90,
        mirror=False,
        bgr=True,
        gamma=False,
        x_offset=0,
        y_offset=0,
    )
    return display


def main():
    backlight = Pin(26, Pin.OUT)
    backlight.on()
    display = _ili9341_init()

    # font = GfxFont("fonts/FreeMono9pt7b.h", scale=2)
    # font = GfxFont("fonts/FreeSans9pt7b.h", scale=2)
    # font = GfxFont("fonts/FreeSans24pt7b.h")
    font = GfxFont("fonts/FreeSansBold24pt7b.h")
    # font = GfxFont("fonts/TomThumb.h", scale=2)

    text = "Hello world!"
    text_w = font.measure_text(text, scale=1)
    x = (320 - text_w) // 2
    y = (240 - font.y_advance) // 2
    display.draw_text(x, y, text, font, color565(255, 255, 255), color565(255, 0, 0), 0)
    display.draw_text8x8(220, 180, "Test Test Test", color565(0, 255, 255))
    display.print("Text", x=50, y=50)
    display.print(" Text2\n")
    display.print("Text3")
    display.print("Test", font=font, color=color565(255, 0, 255), x=180, y=20)
    display.print("Test Test Test Test Test", x=200, y=200)
    display.print("Test Test Test Test Test", x=200, y=220, wrap=False)


if __name__ == "__main__":
    main()
