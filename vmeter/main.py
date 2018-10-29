# -------------------------------------------------------------------------
# Volt-Meter implementation for the Trinket-M0
#
# PIN-setup:
# 0: SDA (I2C-RTC)                    3: digital in (button)
# 1: analog in (voltage)              4: digital in (on/off serial console
# 2: SCL (I2C-RTC)                                   connect to GND to turn on)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/trinket-m0/vmeter
#
# -------------------------------------------------------------------------

import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogOut, AnalogIn

import time

use_rtc = False
if use_rtc:
  import busio as io
  import adafruit_ds3231
  i2c = io.I2C(board.SCL, board.SDA)
  rtc = adafruit_ds3231.DS3231(i2c)

# ---- configure board   --------------------------------------------------

# Built in red LED
led           = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Analog input on D1
v_pin = AnalogIn(board.D1)

# Digital input with pulldown on D3
button           = DigitalInOut(board.D3)
button.direction = Direction.INPUT
button.pull      = Pull.DOWN

# Digital input with pullup on D4 (default is off for serial console)
usbcon           = DigitalInOut(board.D4)
usbcon.direction = Direction.INPUT
usbcon.pull      = Pull.UP

# --- get and convert analog-in   ------------------------------------------

def get_voltage(pin):
  mult = 1.67                              # multiplier for voltage-split
  return (pin.value*mult*3.3)/65536

# --- setup   --------------------------------------------------------------

active     = False
is_pushed  = False
use_usbcon = usbcon.value == 0

# --- main-loop   ----------------------------------------------------------

if use_usbcon:
  print("# starting main-loop")
start = time.monotonic()
last  = start
while True:
  if button.value and not is_pushed:
    active    = not active                     # toggle state
    is_pushed = True                           # check only rising
    time.sleep(0.01)                           # debounce
  elif not button.value and is_pushed:
    is_pushed = False                          # button is released

  if not active:
    led.value = 0
    continue
  else:
    led.value = 1

  # Read analog voltage on D1, and pipe the value to serial console.
  # We don't want to flood the console, so send one measurement every second
  now = time.monotonic()
  if now - last >= 1:
    voltage = get_voltage(v_pin)
    if use_rtc:
      t = rtc.datetime
    if use_usbcon:
      if use_rtc:
        print("%04d%02d%02d-%02d:%02d:%02d %0.2f" %
              (t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min, t.tm_sec,voltage))
      else:
        print("(%0.2f,)" % voltage)
    last = now
