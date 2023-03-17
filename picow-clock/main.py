#-----------------------------------------------------------------------------
# Update time from internet and compare internal and external rtc.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/circuitpython-examples
#-----------------------------------------------------------------------------

import board

# pico
PIN_SDA0  = board.GP16
PIN_SCL0  = board.GP17
PIN_SDA1  = board.GP26
PIN_SCL1  = board.GP27

import time
import displayio
import rtc

from dataviews.Base import Color, Justify
from dataviews.DisplayFactory import DisplayFactory
from dataviews.DataView import DataView

from wifi_impl import WifiImpl as Wifi
from secrets import secrets

# imports for PCF85x3
import busio
#from adafruit_pcf8523 import PCF8523 as PCF_RTC
from adafruit_pcf8563 import PCF8563 as PCF_RTC

# imports for DS3231
import adafruit_ds3231

# create RTCs
i2c  = busio.I2C(PIN_SCL1,PIN_SDA1)
rtcs = [PCF_RTC(i2c),adafruit_ds3231.DS3231(i2c)]

# always release displays (unless you use a builtin-display)
if not hasattr(board,'DISPLAY'):
  displayio.release_displays()

# create display (choose your type!)
if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  display = DisplayFactory.ssd1306(scl=PIN_SCL0,sda=PIN_SDA0)

# create view
view = DataView(
  dim=(len(rtcs)+2,2),
  width=display.width,height=display.height,
  justify=Justify.LEFT,
  bg_color=Color.WHITE,
  color=Color.BLACK,
  formats=["elapsed:", "{0}",
           "PCF8563:", "{0}",
           "DS3231:", "{0}",
           "diff:", "{0}"
           ],
)
display.show(view)
values = (2*len(rtcs)+4)*[None]

# --- format time   ----------------------------------------------------------

def pp_time(hour,min,sec):
  """ pretty-print time """
  return "{0:02d}:{1:02d}:{2:02d}".format(hour,min,sec)

# --- connect to AP   --------------------------------------------------------

def connect():
  """ connect to AP """
  wifi = Wifi(secrets)
  wifi.connect()
  return wifi

# --- main   -----------------------------------------------------------------

# connect and query time
wifi     = connect()
t_js     = wifi.get(secrets['TIMEAPI_URL']).json()
dt_start = time.struct_time(tuple(t_js['struct_time']))

# initialize RTCs
rtc.RTC().datetime = dt_start
for r in rtcs:
  r.datetime = dt_start

ts_start = time.mktime(dt_start)

# update display every second
while True:
  start = time.monotonic()
  tstamps = [rtcs[0].datetime,rtcs[1].datetime]
  values[1] = time.time() - ts_start     # elapsed seconds
  for index in range(len(rtcs)):
    dt = tstamps[index]
    values[2*index+3] = pp_time(dt.tm_hour,dt.tm_min,dt.tm_sec)
  values[7] = time.mktime(tstamps[1]) - time.mktime(tstamps[0])
  view.set_values(values)
  overhead = time.monotonic() - start
  time.sleep(max(0,1-overhead))
