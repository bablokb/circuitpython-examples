# -------------------------------------------------------------------------
# Testprogram for Badger2350 BW e-Paper.
#
# This program is an adaption of Adafruit's uc8151d_simpletest.py from
# https://github.com/adafruit/Adafruit_CircuitPython_UC8151D
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
# -------------------------------------------------------------------------

# pylint: disable=no-member

import time
import board
import displayio

# --- create display (if not builtin)   --------------------------------------

def get_display():
  """ check for builtin display, create otherwise """

  if hasattr(board,"DISPLAY"):
    print("using builtin display")
    return board.DISPLAY

  import busio
  import fourwire
  #from magtag_ssd1680 import SSD1680
  from badger2350_ssd1680 import SSD1680
  #from adafruit_ssd1680 import SSD1680
  #from pimoroni_ssd1680 import SSD1680
  #from waveshare_ssd1680 import SSD1680
  #from wsalt_ssd1680 import SSD1680

  print("releasing displays")
  displayio.release_displays()
  print("done")

  # pinout for Badger2350 display

  SCK_PIN  = board.SCK
  MOSI_PIN = board.MOSI
  MISO_PIN = None
  CS_PIN   = board.INKY_CS
  RST_PIN  = board.INKY_RST
  DC_PIN   = board.INKY_DC
  BUSY_PIN = board.INKY_BUSY

  spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
  display_bus = fourwire.FourWire(
    spi, command=DC_PIN, chip_select=CS_PIN, reset=RST_PIN,
    baudrate=12000000
  )

  print("creating display...")
  return SSD1680(display_bus,
                    busy_pin=BUSY_PIN,
                    rotation=270)


# --- display image   --------------------------------------------------------

def show_image():
  """ show image """

  print("opening image...")
  with open("/display-ruler.bmp", "rb") as f:
    pic = displayio.OnDiskBitmap(f)
    t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
    g.append(t)

    print("refreshing display...")
    start = time.monotonic()
    display.refresh()
    print("...done")
    print("waiting for busy...")
    while display.busy:
      time.sleep(0.05)
    print(f"...finished after {time.monotonic()-start:0.3f}s")

# --- main program   ---------------------------------------------------------

time.sleep(5)
if hasattr(board,'RESET_STATE'):
  print(f"buttons turned on at reset: {board.RESET_STATE():#012b}")
  if board.ON_RESET_PRESSED(board.SW_A):
    print("SW_A pressed!")
  if board.ON_RESET_PRESSED(board.SW_B):
    print("SW_B pressed!")
  if board.ON_RESET_PRESSED(board.SW_C):
    print("SW_C pressed!")
  if board.ON_RESET_PRESSED(board.SW_DOWN):
    print("SW_DOWN pressed!")
  if board.ON_RESET_PRESSED(board.SW_UP):
    print("SW_UP pressed!")
  time.sleep(5)

display = get_display()
g = displayio.Group()
display.root_group = g

show_image()
if hasattr(board,"DISPLAY"):
  for speed in [board.display.SPEED_SLOW, board.display.SPEED_FAST,
                board.display.SPEED_FASTER, board.display.SPEED_FASTEST]:
    time.sleep(5)
    print(f"changing speed to {speed}...")
    board.display.SET_UPDATE_SPEED(speed)
    show_image()
else:
  displayio.release_displays()

while True:
  time.sleep(120)
