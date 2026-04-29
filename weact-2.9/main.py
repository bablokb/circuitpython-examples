# -------------------------------------------------------------------------
# Testprogram for Weact 2.9" BW e-Paper.
#
# This program is an adaption of Adafruit's uc8151d_simpletest.py from
# https://github.com/adafruit/Adafruit_CircuitPython_UC8151D
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

# pylint: disable=no-member

import time
import board
import busio
import displayio
import fourwire
import adafruit_ssd1680

displayio.release_displays()

# pinout for WeAct 2.9" display

SCK_PIN  = board.GP14
MOSI_PIN = board.GP15
MISO_PIN = None
CS_PIN   = board.GP13
RST_PIN  = board.GP10
DC_PIN   = board.GP11
BUSY_PIN = board.GP12

spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
display_bus = fourwire.FourWire(
  spi, command=DC_PIN, chip_select=CS_PIN, reset=RST_PIN, baudrate=1000000
)

display = adafruit_ssd1680.SSD1680(display_bus,
                                   busy_pin=BUSY_PIN,
                                   width=296,height=128,rotation=270)

g = displayio.Group()
display.root_group = g

with open("/display-ruler.bmp", "rb") as f:
  pic = displayio.OnDiskBitmap(f)
  t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
  g.append(t)

  display.refresh()
  time.sleep(120)
