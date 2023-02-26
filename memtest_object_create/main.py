# -------------------------------------------------------------------------
# Test memory for object-creation
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import gc
import board
import busio

PIN_SDA  = board.GP2
PIN_SCL  = board.GP3

gc.collect()
print("free mem before import: %s" % gc.mem_free())

from adafruit_pcf8563 import PCF8563
gc.collect()
print("free mem after import: %s" % gc.mem_free())

i2c = busio.I2C(PIN_SCL,PIN_SDA)
rtc = PCF8563(i2c)
gc.collect()
print("free mem after constructor: %s" % gc.mem_free())
