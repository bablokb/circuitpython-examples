# SPDX-FileCopyrightText: 2025 Bernhard Bablok
#
# SPDX-License-Identifier: MIT
"""
`badger2350_ssd1680`
================================================================================

CircuitPython `displayio` driver for Badger2350-SSD1680


* Author(s): Bernhard Bablok

"""

from epaperdisplay import EPaperDisplay

try:
  import typing
  from fourwire import FourWire
except ImportError:
  pass

SPEED = 1

# 5x12 = 60 bytes
_LUT_START = (
  b"\x40\x68\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" # VS L0
  b"\xA0\x65\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" # VS L1
  b"\xA8\x65\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00" # VS L2
  b"\xAA\x65\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00" # VS L3
  b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" # VS L4
  )

# every entry will have an added byte at the end for the repeat-count
# so total count is 21 bytes
_LUT_REPEAT = (
  b"\x02\x00\x00\x05\x0A\x00"    # Group0
) + SPEED.to_bytes(1,'little') + (
  b"\x19\x19\x00\x02\x00\x00"    # Group1
) + SPEED.to_bytes(1,'little') + (
  b"\x05\x0A\x00\x00\x00\x00"    # Group2
) + SPEED.to_bytes(1,'little')

# 10x7 +2 = 72 bytes
_LUT_END = (
  b"\x00\x00\x00\x00\x00\x00\x00" # Group3
  b"\x00\x00\x00\x00\x00\x00\x00" # Group4
  b"\x00\x00\x00\x00\x00\x00\x00" # Group5
  b"\x00\x00\x00\x00\x00\x00\x00" # Group6
  b"\x00\x00\x00\x00\x00\x00\x00" # Group7
  b"\x00\x00\x00\x00\x00\x00\x00" # Group8
  b"\x00\x00\x00\x00\x00\x00\x00" # Group9
  b"\x00\x00\x00\x00\x00\x00\x00" # Group10
  b"\x00\x00\x00\x00\x00\x00\x00" # Group11
  b"\x44\x42\x22\x22\x23\x32\x00" # Config
  b"\x00\x00"                     # FR, XON
)

_START_SEQUENCE = (
  b"\x12\x80\x00\x14"              # SWR soft reset and wait 20ms (DS: 10ms)
  b"\x11\x00\x01\x03"              # DEM Ram data entry mode 0b011
  b"\x3c\x00\x01\x03"              # BWCTL border color (0: black, 5: gray/white?)
  b"\x2c\x00\x01\x28"              # WVCOM
  b"\x03\x00\x01\x17"              # GDVC
  b"\x04\x00\x03\x41\xae\x32"      # SDVC
  b"\x4e\x00\x01\x00"              # SRXC ram x address
  b"\x4f\x00\x02\x00\x00"          # SRYC ram y address (0)
  b"\x01\x00\x03\x07\x01\x00"      # DOC set display size x0107 = 264-1 lines
  #b"\x44\x00\x02\x00\x15"          # SRX set RAM x-start (POR, x15 = 176/8-1 cols)
  #b"\x45\x00\x04\x00\x00\x07\x01"  # SRY set RAM y-start (0-263)

) + (
  b"\x32\x00\x99"                  # WLR with x99=153 bytes and delay of 500ms
) + _LUT_START+_LUT_REPEAT+_LUT_END + (

  b"\x22\x00\x01\xC7"          # DUC2

  #b"\x7f\x80\x00\xff"
  #b"\x3f\x00\x01\x22"              # EOPT
)

_REFRESH_SEQUENCE = (
  #b"\x0c\x00\x00"              # BTST
  b"\x20\x00\x00"              # ADUS
)

# DSM1: 1µA, DSM2: 0.7µA (DSM1 keeps RAM)
_STOP_SEQUENCE = b"\x10\x00\x01\x01"  # DSM Deep Sleep Mode 1

# pylint: disable=too-few-public-methods
class SSD1680(EPaperDisplay):
  r"""SSD1680 driver

  :param bus: The data bus the display is on
  :Keyword Arguments:
    * *speed* (``int``) --
      Update speed (0-3, 0: slowest, default: 1)
  """

  def __init__(
    self, bus: FourWire, height=176, width=264, **kwargs
   ) -> None:
    bus.reset()

    super().__init__(
      bus,
      _START_SEQUENCE,
      _STOP_SEQUENCE,
      **kwargs,
      height=height,
      width=width,
      ram_width=250,
      ram_height=296,
      busy_state=True,
      grayscale=True,
      black_bits_inverted=False,
      color_bits_inverted=True,
      highlight_color=0xFF2121,
      write_black_ram_command=0x24,
      write_color_ram_command=0x26,
      set_column_window_command=0x44,
      set_row_window_command=0x45,
      set_current_column_command=0x4E,
      set_current_row_command=0x4F,
      refresh_display_command=_REFRESH_SEQUENCE,
      always_toggle_chip_select=False,
      two_byte_sequence_length=True,
      address_little_endian=True,
      seconds_per_frame=3,
      )
