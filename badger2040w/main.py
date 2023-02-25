# -------------------------------------------------------------------------
# Testprogram for Pimoroni's Badger2040W
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import time
import board
import busio
import displayio

display = board.DISPLAY

g = displayio.Group()

with open("/display-ruler.bmp", "rb") as f:
  pic = displayio.OnDiskBitmap(f)
  t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
  g.append(t)

  display.show(g)
  display.refresh()
  time.sleep(120)
