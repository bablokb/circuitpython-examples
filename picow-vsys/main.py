#-----------------------------------------------------------------------------
# Measure VSYS and print result
#
# Author: Bernhard Bablok
#
# Website: https://github.com/circuitpython-examples
#-----------------------------------------------------------------------------

import board
import time
from analogio import AnalogIn
import busio
import displayio

from dataviews.Base import Color, Justify
from dataviews.DisplayFactory import DisplayFactory
from dataviews.DataView import DataView

# always release displays (unless you use a builtin-display)
if not hasattr(board,'DISPLAY'):
  displayio.release_displays()

# create display
if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  display = DisplayFactory.st7789(
    pin_dc=board.GP16,
    pin_cs=board.GP17,
    spi=busio.SPI(clock=board.GP18,MOSI=board.GP19)
  )

# create sensor
adc = AnalogIn(board.VOLTAGE_MONITOR)

# create view with one row for voltage
view = DataView(
  dim=(1,1),
  width=display.width,height=display.height,
  justify=Justify.CENTER,
  fontname="fonts/DejaVuSansMono-Bold-32-subset.bdf",
  formats=["{0:.1f}V"],
  border=1,
  divider=0,
  padding=10,
)
display.show(view)

values = [0]
while True:
  values[0] = adc.value *  3 * 3.3 / 65535
  view.set_values(values)
  time.sleep(5)
