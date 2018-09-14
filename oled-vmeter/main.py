# -------------------------------------------------------------------------
# Volt-Meter implementation for the Trinket-M0 with a 128x64 OLED display
#
# PIN-setup:
# 0: SDA (I2C-OLED)                   3: digital in (button)
# 1: analog in (voltage)              4:
# 2: SCL (I2C-OLED)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/m0-oled-vmeter
#
# -------------------------------------------------------------------------

import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogOut, AnalogIn

import time

# ---- configure board   --------------------------------------------------

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Analog input on D1
v_pin = AnalogIn(board.D1)

# Digital input with pulldown on D3
button = DigitalInOut(board.D3)
button.direction = Direction.INPUT
button.pull = Pull.DOWN

# --- get and convert analog-in   ------------------------------------------

def get_voltage(pin):
  mult = 1.0                              # multiplier for voltage-split
  return (pin.value*mult*3.3)/65536

# --- display voltage on the OLED   ----------------------------------------

def display_voltage(v):
  pass

# --- main-loop   ----------------------------------------------------------

active    = False
is_pushed = False

print("starting main-loop")
start = time.monotonic()
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

  # Read analog voltage on D1, and pipe the value to serial console
  voltage = get_voltage(v_pin)
  print("%0.5f: %0.2f" % (time.monotonic()-start,voltage))
  display_voltage(voltage)
