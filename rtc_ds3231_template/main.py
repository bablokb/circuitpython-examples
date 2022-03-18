# -------------------------------------------------------------------------
# rtc_ds3231_template/main.py: template for DS3231 RTC
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuit-python-examples
#
# -------------------------------------------------------------------------

import time
import gc

print("free: %s" % gc.mem_free())

import board
import busio as io
import adafruit_ds3231

i2c = io.I2C(board.SCL, board.SDA)
rtc = adafruit_ds3231.DS3231(i2c)
print("free: %s" % gc.mem_free())

t = rtc.datetime
print("current time: %02d:%02d:%02d" % (t.tm_hour,t.tm_min, t.tm_sec))
