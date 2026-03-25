# ----------------------------------------------------------------------------
# An abstract clock using a ring of 60 neopixels.
#
# Author: Bernhard Bablok
# License: MIT
#
# Website: https://github.com/bablokb/circuitpython-examples
# ----------------------------------------------------------------------------

import atexit
import board
import neopixel
import rtc
import time

# board.DATA is defined for Pimoroni Plasma-boards. Adapt for your own needs

pixel_pin  = board.DATA
num_pixels = 60

def at_exit(pixels):
  """ turn of strip and free ressources """
  print("at_exit(): deinit strip")
  pixels.deinit()

# --- clock colors   ---------------------------------------------------------

COLOR_SEC = (0,255,255)
COLOR_MIN = (255,255,0)
COLOR_STD = (255,0,0)

# --- main program   ---------------------------------------------------------

# max 180mA with brightness=0.1
# max 105mA with brightness=0.05
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                           brightness=0.05, auto_write=False)
atexit.register(at_exit,pixels)

# set the RTC to something valid
# N.B: replace with an update based on internet time

rtc.RTC().datetime = time.struct_time((2026,3,25, 15,22,0,2,84,0))

while True:
  start = time.monotonic()
  pixels.fill(0)
  ts = time.localtime()
  #print(f"setting ({ts.tm_hour%12*5+ts.tm_min//12},{ts.tm_min},0-{ts.tm_sec})")
  for i in range(ts.tm_sec):
    pixels[i] = COLOR_SEC
  pixels[ts.tm_min] = COLOR_MIN
  pixels[ts.tm_hour%12*5+ts.tm_min//12] = COLOR_STD
  pixels.show()
  time.sleep(1 - (time.monotonic()-start))
