#-----------------------------------------------------------------------------
# Test Ram-Byte of Badger2040W/PCF85063A
#
# Author: Bernhard Bablok
#
# Website: https://github.com/circuitpython-examples
#-----------------------------------------------------------------------------

import board
import time
import busio
import displayio
import pcf85063a

from dataviews.Base import Color, Justify
from dataviews.DisplayFactory import DisplayFactory
from dataviews.DataView import DataView

# create RTC
i2c = board.I2C()
rtc = pcf85063a.PCF85063A(i2c)

# create display
display = board.DISPLAY

# create view with one row for ram_byte
view = DataView(
  dim=(1,1),
  width=display.width,height=display.height,
  justify=Justify.CENTER,
  fontname="fonts/DejaVuSansMono-Bold-32-subset.bdf",
  formats=["{0}"],
  border=1,
  divider=0,
  padding=10,
)
display.show(view)

# get ram-byte and display value
val = rtc.ram_byte
values = [val]
view.set_values(values)
display.refresh()
time.sleep(3)

# update value
val = (val+1)%256
rtc.ram_byte = val

# shutdown
board.ENABLE_DIO.value = 0
