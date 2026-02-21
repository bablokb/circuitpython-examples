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
import busio
import displayio
import fourwire

#from magtag_ssd1680 import SSD1680
from badger2350_ssd1680 import SSD1680
#from adafruit_ssd1680 import SSD1680
#from pimoroni_ssd1680 import SSD1680
#from waveshare_ssd1680 import SSD1680
#from wsalt_ssd1680 import SSD1680

time.sleep(5)
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
display = SSD1680(display_bus,
                  busy_pin=BUSY_PIN,
                  rotation=270)

g = displayio.Group()
display.root_group = g

print("opening image...")
with open("/display-ruler.bmp", "rb") as f:
  pic = displayio.OnDiskBitmap(f)
  t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
  g.append(t)

  print("refreshing display...")
  display.refresh()
  print("...done")
  while display.busy:
    print("busy...")
    time.sleep(1)
  print("...finished")

  #   time.sleep(4)
  #   print("rotating display...")
  #   display.rotation = 270
  #   display.refresh()
  #   print("...done")
  #   while display.busy:
  #     print("busy...")
  #     time.sleep(1)
  #   print("...finished")

displayio.release_displays()
while True:
  time.sleep(120)
