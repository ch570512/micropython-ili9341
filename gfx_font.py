# GFX fonts for rdagger/micropython-ili9341
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

import gc
import micropython
from array import array
from micropython import const

_GOFF = const(0)  # bitmapOffset
_GW = const(1)  # width
_GH = const(2)  # height
_GXA = const(3)  # xAdvance
_GXO = const(4)  # xOffset
_GYO = const(5)  # yOffset
_GLYPH_SLOT = const(6)  # fields per glyph


class GfxFont:
    """Load font data in Adafruit GFX format."""

    def __init__(self, path: str, scale: int = 1):
        self.scale: int = scale
        self.bitmaps: bytearray = bytearray()
        self.glyphs = array("i")
        self.first_char: int = 0x20
        self.last_char: int = 0x7E
        self.y_advance: int = 0
        self.letter_count: int = 0
        self._max_ascent: int = 0

        self.__load_gfx_font(path)

        # Total number of glyphs in the font table
        self.letter_count = len(self.glyphs) // _GLYPH_SLOT

        # Calculate max ascent
        if len(self.glyphs) >= _GLYPH_SLOT:
            y_offsets = (
                self.glyphs[i + _GYO] for i in range(0, len(self.glyphs), _GLYPH_SLOT)
            )
            self._max_ascent = -min(y_offsets)

        gc.collect()

    @staticmethod
    def _parse_hex_line(line: str, bitmaps: bytearray) -> None:
        """Parse comma-separated hex values and append to bytearray."""
        idx = line.find("//")
        if idx >= 0:
            line = line[:idx]

        line = line.strip()
        if not line:
            return

        if line.endswith(","):
            line = line[:-1]

        for token in line.split(","):
            token = token.strip()
            if token.startswith("0x") or token.startswith("0X"):
                bitmaps.append(int(token, 16))

    @staticmethod
    def _parse_glyph_line(line: str) -> tuple | None:
        """Extract GFXglyph struct values into a tuple."""
        if "{" not in line:
            return None

        idx = line.find("//")
        content = line[:idx] if idx >= 0 else line

        if "{" in content:
            content = content[content.index("{") + 1 :]
        if "}" in content:
            content = content[: content.index("}")]

        parts = []
        for token in content.split(","):
            token = token.strip()
            if not token or "(" in token:
                continue
            try:
                parts.append(int(token, 0))
            except ValueError:
                pass

        return tuple(parts[:6]) if len(parts) >= 6 else None

    @staticmethod
    def _parse_font_info_line(line: str) -> tuple | None:
        """Extract font info values (first_char, last_char, yAdvance)."""
        if "(uint8_t" not in line and "(GFXglyph" not in line:
            return None

        idx = line.find("//")
        content = line[:idx] if idx >= 0 else line
        content = content.replace("{", "").replace("}", "").replace(";", "")

        values = []
        for p in content.split(","):
            p = p.strip()
            if not p or "(" in p:
                continue
            try:
                values.append(int(p, 0))
            except ValueError:
                pass

        return (values[0], values[1], values[2]) if len(values) >= 3 else None

    def __load_gfx_font(self, path: str) -> None:
        """Parse GFX header file line by line."""
        in_bitmaps = False
        in_glyphs = False
        font_found = False
        info_acc = ""
        collecting_info = False

        with open(path, "r") as f:
            for line in f:
                stripped = line.strip()

                # Parse Bitmaps
                if "uint8_t" in stripped and "{" in stripped:
                    in_bitmaps = True
                    if "}" in stripped:
                        in_bitmaps = False
                    brace_pos = stripped.index("{")
                    self._parse_hex_line(stripped[brace_pos + 1 :], self.bitmaps)
                    continue

                if in_bitmaps:
                    if "}" in stripped:
                        brace_pos = stripped.index("}")
                        self._parse_hex_line(stripped[:brace_pos], self.bitmaps)
                        in_bitmaps = False
                        continue
                    self._parse_hex_line(stripped, self.bitmaps)

                # Parse Glyphs
                if "GFXglyph" in stripped and "{" in stripped:
                    in_glyphs = True
                    if "}" in stripped and stripped.strip().endswith("};"):
                        in_glyphs = False
                    g = self._parse_glyph_line(stripped)
                    if g:
                        self.glyphs.extend(g)
                    continue

                if in_glyphs:
                    if (
                        "};" in stripped
                        or stripped.endswith("};")
                        or (stripped.endswith("}") and not stripped.endswith("},"))
                    ):
                        brace_pos = stripped.index("}")
                        g = self._parse_glyph_line(stripped[:brace_pos])
                        if g:
                            self.glyphs.extend(g)
                        in_glyphs = False
                        continue
                    g = self._parse_glyph_line(stripped)
                    if g:
                        self.glyphs.extend(g)

                # Parse Font Info
                if not font_found and ("GFXfont" in stripped or collecting_info):
                    if not collecting_info:
                        collecting_info = True
                        info_acc = stripped
                    else:
                        info_acc += " " + stripped

                    if ");" in info_acc or (
                        info_acc.count("{") > 0 and "}" in info_acc and ";" in info_acc
                    ):
                        fi = self._parse_font_info_line(info_acc)
                        if fi:
                            self.first_char = fi[0]
                            self.last_char = fi[1]
                            self.y_advance = fi[2]
                            font_found = True

    @micropython.native
    def get_letter(
        self, letter: str, color: int, background: int = 0, landscape: bool = False
    ) -> tuple:
        """Render a single character into a bytearray."""
        letter_ord = ord(letter)
        glyph_idx = letter_ord - self.first_char

        if glyph_idx < 0 or glyph_idx >= self.letter_count:
            print("Missing char:", letter)
            return b"", 0, 0

        base = glyph_idx * _GLYPH_SLOT
        glyps = self.glyphs
        w = glyps[base + _GW]
        h = glyps[base + _GH]
        x_adv = glyps[base + _GXA]
        x_off = glyps[base + _GXO]
        sf = self.scale
        c_msb = (color >> 8) & 0xFF
        c_lsb = color & 0xFF
        buf_w = x_adv * sf
        buf_h = self.y_advance * sf
        start_col = x_off * sf
        start_row = (self._max_ascent + glyps[base + _GYO]) * sf
        buf = bytearray(buf_w * buf_h * 2)

        if background:
            bg_msb = (background >> 8) & 0xFF
            bg_lsb = background & 0xFF
            for i in range(0, len(buf), 2):
                buf[i] = bg_msb
                buf[i + 1] = bg_lsb

        bitmaps = self.bitmaps
        bm_len = len(bitmaps)
        bm_pos = glyps[base + _GOFF]
        bit_cnt = 0
        bits = 0

        if not landscape:
            for py in range(h):
                dst_row = start_row + py * sf
                for px in range(w):
                    if bit_cnt == 0:
                        bits = bitmaps[bm_pos] if bm_pos < bm_len else 0
                        bm_pos += 1
                    pixel_on = bits & 0x80
                    bits <<= 1
                    bit_cnt += 1
                    if bit_cnt == 8:
                        bit_cnt = 0

                    if pixel_on:
                        dst_col = start_col + px * sf
                        for dy in range(sf):
                            r = dst_row + dy
                            base_idx = r * buf_w + dst_col
                            for dx in range(sf):
                                idx = (base_idx + dx) << 1
                                buf[idx] = c_msb
                                buf[idx + 1] = c_lsb
        else:
            for py in range(h):
                dst_row = start_row + py * sf
                for px in range(w):
                    if bit_cnt == 0:
                        bits = bitmaps[bm_pos] if bm_pos < bm_len else 0
                        bm_pos += 1
                    pixel_on = bits & 0x80
                    bits <<= 1
                    bit_cnt += 1
                    if bit_cnt == 8:
                        bit_cnt = 0

                    if pixel_on:
                        dst_col = start_col + px * sf
                        for dy in range(sf):
                            r = dst_row + dy
                            for dx in range(sf):
                                p = (buf_w - 1 - (dst_col + dx)) * buf_h + r
                                idx = p << 1
                                buf[idx] = c_msb
                                buf[idx + 1] = c_lsb

        return buf, buf_w, buf_h

    def measure_text(self, text: str) -> int:
        """Measure pixel width of text string."""
        total = 0
        first = self.first_char
        last = self.last_char
        glyps = self.glyphs
        glyph_count = len(glyps) // _GLYPH_SLOT
        sf = self.scale

        for ch in text:
            ch_ord = ord(ch)
            if first <= ch_ord <= last:
                gi = ch_ord - first
                if gi < glyph_count:
                    total += glyps[gi * _GLYPH_SLOT + _GXA] * sf

        return total
