# ----------------------------------------------------------------------------
# Testprogram for ens160.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# ----------------------------------------------------------------------------

INTERVAL_STARTUP = 48*3600    # 48 hours
INTERVAL_WARMUP  = 30         # 1 minute
INTERVAL_NORMAL  = 30        # measurement interval

import time
import board
import displayio

from dataviews.Base import Justify
from dataviews.DisplayFactory import DisplayFactory
from dataviews.DataView import DataView

import busio
import adafruit_ens160
import adafruit_ahtx0

# always release displays (unless you use a builtin-display)
if not hasattr(board,'DISPLAY'):
  displayio.release_displays()

# XIAO RP2040 with expansion board and RTC8563
PIN_SDA  = board.SDA
PIN_SCL  = board.SCL

# create devices
i2c    = busio.I2C(PIN_SCL,PIN_SDA)
aht20  = adafruit_ahtx0.AHTx0(i2c)
ens160 = adafruit_ens160.ENS160(i2c)
time.sleep(5)                            # wait for device init

# create display (choose your type!)
if hasattr(board,'DISPLAY'):
  display = board.DISPLAY
else:
  display = DisplayFactory.ssd1306(i2c)

# create view
view = DataView(
  dim=(4,2),
  width=display.width,height=display.height,
  justify=Justify.RIGHT,
  formats=["Stat:","{0}",
           "AQI:", "{0}",
           "TVOC:", "{0}",
           "eCO2:", "{0}"
           ],
  border=1,
  divider=1,
  padding=1,
)

# realign only fields in first column
for index in [0,2,4,6]:
  view.justify(Justify.LEFT,index)

display.root_group = view

counter_3 = 0
counter_2 = 0
counter_1 = 0

print("starting measurements")
while True:
  # read sensors

  status = ens160.data_validity

  # no valid output (should not happen?!)
  if status == 3:
    print(f"status: {status} - invalid data\n")
    counter_3 += 1
    view.set_values(
      [None, status,
       None, counter_3,
       None, 0,
       None, 0]
      )
    time.sleep(INTERVAL_NORMAL)
    continue

  # initial startup (takes 48h)
  elif status == 2:
    print(f"status: {status} - initial startup\n")
    counter_2 += 1
    view.set_values(
      [None, status,
       None, counter_2,
       None, 0,
       None, 0]
      )
    if counter_2 == 1:
      print(f"sleeping {INTERVAL_STARTUP}")
      time.sleep(INTERVAL_STARTUP)
    else:
      print(f"sleeping {INTERVAL_NORMAL}")
      time.sleep(INTERVAL_NORMAL)
    continue

  # warmup (takes 1-3 minutes)
  elif status == 1:
    print(f"status: {status} - warmup\n")
    counter_1 += 1
    view.set_values(
      [None, status,
       None, counter_1,
       None, 0,
       None, 0]
      )
    print(f"sleeping {INTERVAL_WARMUP}")
    time.sleep(INTERVAL_WARMUP)
    continue

  # standard operation mode
  else:
    print(f"status: {status} - normal operation")

    t = aht20.temperature
    h = aht20.relative_humidity
    print(f"temp: {t:.1f}°C")
    print(f"hum:  {h:.0f}%rH")

    ens160.temperature_compensation = t
    ens160.humidity_compensation    = h
    if ens160.new_data_available:
      data   = ens160.read_all_sensors()
      print(f"AQI:  {data['AQI']}")
      print(f"TVOC: {data['TVOC']}")
      print(f"eCO2: {data['eCO2']}")
      view.set_values(
        [None, status,
         None, data["AQI"],
         None, data["TVOC"],
         None, data["eCO2"]
         ]
      )
    time.sleep(INTERVAL_NORMAL)
