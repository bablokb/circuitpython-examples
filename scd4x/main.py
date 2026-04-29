# ----------------------------------------------------------------------------
# Testprogram for SCD4x CO2-sensors.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# ----------------------------------------------------------------------------

INTERVAL = 60

import time
import board
import displayio

from dataviews.Base import Justify
from dataviews.DisplayFactory import DisplayFactory
from dataviews.DataView import DataView

import busio
from scd4x import SCD4X

# always release displays (unless you use a builtin-display)
if not hasattr(board,'DISPLAY'):
  displayio.release_displays()

# XIAO RP2040 with expansion board and RTC8563
PIN_SDA  = board.SDA
PIN_SCL  = board.SCL

# create devices
i2c    = busio.I2C(PIN_SCL,PIN_SDA)
scd4x  = SCD4X(None,[(i2c,0)])
#time.sleep(5)                            # wait for device init

# create display (choose your type!)
if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  display = DisplayFactory.ssd1306(i2c)

# create view for 4 measurments
view = DataView(
  dim=(4,2),
  width=display.width,height=display.height,
  justify=Justify.RIGHT,
  formats=["{0}","{0}",
           "{0}", "{0}",
           "{0}", "{0}",
           "{0}", "{0}"
           ],
  border=1,
  divider=1,
  padding=1,
)

display.root_group = view

data = {}
values = []
print("starting measurements")
while True:
  # read sensors

  results = scd4x.read(data,values).split(',')
  view.set_values(results)

  time.sleep(INTERVAL)
