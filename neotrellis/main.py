# -------------------------------------------------------------------------
# Neotrellis.
#
# Adapted from example neotrellis_simpletest.py for the pico.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis

# create the i2c object for the trellis
SCL     = board.GP27
SDA     = board.GP26
i2c_bus = busio.I2C(SCL, SDA)

# create the trellis
trellis = NeoTrellis(i2c_bus)

# some color definitions
OFF    = (0, 0, 0)
ON     = (255, 255, 255)
RED    = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN  = (0, 255, 0)
CYAN   = (0, 255, 255)
BLUE   = (0, 0, 255)
PURPLE = (180, 0, 255)

# default color-layout
defpix = [
  YELLOW,YELLOW,YELLOW,ON,
  YELLOW,BLUE  ,YELLOW,ON,
  YELLOW,YELLOW,YELLOW,ON,
  GREEN, BLUE,  RED,   ON
  ]

# this will be called when button events are received
def on_btn(event):
    # switch to cyan when a rising edge is detected
    if event.edge == NeoTrellis.EDGE_RISING:
        trellis.pixels[event.number] = CYAN
    # reset when a falling edge is detected
    elif event.edge == NeoTrellis.EDGE_FALLING:
        trellis.pixels[event.number] = defpix[event.number]


for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the on_btn callback
    trellis.callbacks[i] = on_btn

    # cycle the LEDs on startup
    trellis.pixels[i] = PURPLE
    time.sleep(0.05)

for i in range(16):
    trellis.pixels[i] = defpix[i]
    time.sleep(0.05)

while True:
    # call the sync function call any triggered callbacks
    trellis.sync()
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)
