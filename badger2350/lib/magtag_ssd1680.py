from epaperdisplay import EPaperDisplay

try:
  import typing
  from fourwire import FourWire
except ImportError:
  pass

_START_SEQUENCE = (
  b"\x12\x80\x00\x14"                 # soft reset and wait 20ms
  b"\x11\x00\x01\x03"                 # Ram data entry mode
  b"\x3c\x00\x01\x03"                 # border color
  b"\x2c\x00\x01\x28"                 # Set vcom voltage
  b"\x03\x00\x01\x17"                 # Set gate voltage
  b"\x04\x00\x03\x41\xae\x32"         # Set source voltage
  b"\x4e\x00\x01\x00"                 # ram x count
  b"\x4f\x00\x02\x00\x00"             # ram y count
  b"\x01\x00\x03\x07\x01\x00"         # set display size

  b"\x32\x00\x99"                     # Update waveforms
  b"\x2a\x60\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00"     # VS L0
  b"\x20\x60\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00"     # VS L1
  b"\x28\x60\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00"     # VS L2
  b"\x00\x60\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"     # VS L3
  b"\x00\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"     # VS L4

  b"\x00\x02\x00\x05\x14\x00\x00"             # TP, SR, RP of Group0
  b"\x1E\x1E\x00\x00\x00\x00\x01"             # TP, SR, RP of Group1
  b"\x00\x02\x00\x05\x14\x00\x00"             # TP, SR, RP of Group2
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group3

  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group4
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group5
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group6
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group7
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group8
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group9
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group10
  b"\x00\x00\x00\x00\x00\x00\x00"             # TP, SR, RP of Group11
  b"\x24\x22\x22\x22\x23\x32\x00\x00\x00"     # FR, XON

  b"\x22\x00\x01\xc7"                         # display update mode
)

_REFRESH_SEQUENCE = b"\x20\x00\x00"
_STOP_SEQUENCE = b"\x10\x80\x01\x01\x64"  # Deep Sleep

# pylint: disable=too-few-public-methods
class SSD1680(EPaperDisplay):
  r"""SSD1680 driver

  :param bus: The data bus the display is on
  :param \**kwargs:
    See below
    """

  def __init__(self, bus: FourWire, **kwargs) -> None:
    bus.reset()
    super().__init__(
      bus,
      _START_SEQUENCE,
      _STOP_SEQUENCE,
      **kwargs,
      width=264,
      height=176,
      #colstart=8,  
      ram_width=250,
      ram_height=296,
      busy_state=True,
      grayscale=True,
      seconds_per_frame=3,
      refresh_time=1,
      write_black_ram_command=0x24,
      write_color_ram_command=0x26,
      set_column_window_command=0x44,
      set_row_window_command=0x45,
      set_current_column_command=0x4E,
      set_current_row_command=0x4F,
      refresh_display_command=_REFRESH_SEQUENCE,
      always_toggle_chip_select=False,
      #address_little_endian=True,
      two_byte_sequence_length=True,
      )
