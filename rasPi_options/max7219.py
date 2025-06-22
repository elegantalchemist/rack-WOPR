"""
MicroPython max7219 cascadable 8x8 LED matrix driver
https://github.com/mcauser/micropython-max7219

MIT License
Copyright (c) 2017 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
import framebuf

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

class Matrix8x8:
  def __init__(self, spi, cs, num):
    """
    Driver for cascading MAX7219 8x8 LED matrices.

    >>> import max7219
    >>> from machine import Pin, SPI
    >>> spi = SPI(1)
    >>> display = max7219.Matrix8x8(spi, Pin('X5'), 4)
    >>> display.text('1234',0,0,1)
    >>> display.show()

    """
    self.spi = spi
    self.cs = cs
    self.cs.init(cs.OUT, True)
    self.buffer = bytearray(8 * num)
    self.num = num
    fb = framebuf.FrameBuffer(self.buffer, 8 * num, 8, framebuf.MONO_HLSB)
    self.framebuf = fb
    # Provide methods for accessing FrameBuffer graphics primitives. This is a workround
    # because inheritance from a native class is currently unsupported.
    # http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
    self.fill = fb.fill  # (col)
    self.pixel = fb.pixel # (x, y[, c])
    self.hline = fb.hline  # (x, y, w, col)
    self.vline = fb.vline  # (x, y, h, col)
    self.line = fb.line  # (x1, y1, x2, y2, col)
    self.rect = fb.rect  # (x, y, w, h, col)
    self.fill_rect = fb.fill_rect  # (x, y, w, h, col)
    self.text = fb.text  # (string, x, y, col=1)
    self.scroll = fb.scroll  # (dx, dy)
    self.blit = fb.blit  # (fbuf, x, y[, key])
    self.init()

  def _write(self, command, data):
    self.cs(0)
    for m in range(self.num):
      self.spi.write(bytearray([command, data]))
    self.cs(1)

  def init(self):
    for command, data in (
      (_SHUTDOWN, 0),
      (_DISPLAYTEST, 0),
      (_SCANLIMIT, 7),
      (_DECODEMODE, 0),
      (_SHUTDOWN, 1),
    ):
      self._write(command, data)

  def brightness(self, value):
    if not 0 <= value <= 15:
      raise ValueError("Brightness out of range")
    self._write(_INTENSITY, value)

  def show(self):
    for y in range(8):
      self.cs(0)
      for m in range(self.num):
        self.spi.write(bytearray([_DIGIT0 + y, self.buffer[(y * self.num) + m]]))
      self.cs(1)
  
  def shift_region(self, x, y, w, h, shift, wrap=True):
    """
    Shift a rectangular region in a framebuf horizontally.

    x, y: top-left pixel coordinate of the rectangle.
    w, h: width and height of the region.
    shift: number of pixels to shift (positive: right, negative: left).
    wrap: if True, pixels shifted off one end wrap around; otherwise, zeros fill in.
    """

    full_width = 8 * self.num
    # Calculate number of bytes per row (each byte holds 8 pixels)
    row_byte_width = (full_width + 7) // 8

    for row in range(y, y + h):
        row_start = row * row_byte_width
        row_bytes = self.buffer[row_start:row_start + row_byte_width]
        row_bits = ''.join(f"{b:08b}" for b in row_bytes)[:full_width]

        # Extract the bits corresponding to the rectangle in this row
        region_bits = row_bits[x:x+w]

        # Shift the bits inside the rectangle
        if shift > 0: # Right shift
            if wrap:
                new_region = region_bits[-shift:] + region_bits[:-shift]
            else:
                new_region = ('0' * shift) + region_bits[:-shift]
        elif shift < 0: # Left shift
            shift_abs = -shift
            if wrap:
                new_region = region_bits[shift_abs:] + region_bits[:shift_abs]
            else:
                new_region = region_bits[shift_abs:] + ('0' * shift_abs)
        else:
            new_region = region_bits

        # Reassemble the full row's bit string:
        new_row_bits = row_bits[:x] + new_region + row_bits[x+w:]

        new_row_bytes = bytearray()
        for i in range(0, len(new_row_bits), 8):
            bits_group = new_row_bits[i:i+8]
            if len(bits_group) < 8:
                bits_group = bits_group.ljust(8, '0')
            new_row_bytes.append(int(bits_group, 2))

        # Update the framebuffer row with the new bytes
        self.buffer[row_start:row_start + row_byte_width] = new_row_bytes
