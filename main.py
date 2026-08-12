# micropython-ili9341_next
# Copyright (C) 2026 by ch570512
# @created 25.07.2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT license.

from machine import Pin, SPI
from ili9341 import Display, color565
from gfx_font import GfxFont


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

    text = "Hello world!xxxx"
    text_w = font.measure_text(text)
    x = (320 - text_w) // 2
    y = (240 - font.y_advance * font.scale) // 2
    display.draw_text(
        x, y, text, font, color565(255, 255, 255), color565(255, 0, 0), False, False, 1
    )
    display.draw_text8x8(220, 180, "Test Test Test", color565(0, 255, 255))
    display.print("Text", x=50, y=50)
    display.print(" Text2\n")
    display.print("Text3")
    display.print("Test", font=font, color=color565(255, 0, 255), x=180, y=20)
    display.print("Test Test Test Test Test", x=200, y=200)


if __name__ == "__main__":
    main()
