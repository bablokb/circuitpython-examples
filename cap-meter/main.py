# ----------------------------------------------------------------------------
# cmeter-cipy.py: measure capacity using CircuitPython
#
# Author: Bernhard Bablok
# License: GPL3
#
# See the file schematic.png for the circuit. You need a fast-discharge
# resistor connected to board.D1, a load resistor connected to board.D0
# with known R-value and a capacitor with unknown capacitance. Configure
# the value of R in the program.
#
# Note that R*C is the time of a single measurement, this should be neither
# too large nor too small.
#
# Website: https://github.com/bablokb/circuit-python-examples
#
# ----------------------------------------------------------------------------

import board
from digitalio import DigitalInOut, Direction
from analogio  import AnalogIn
import time

# Trinket-M0
#PIN_CHARGE    = DigitalInOut(board.D0)
#PIN_DISCHARGE = DigitalInOut(board.D1)
#PIN_ADC       = AnalogIn(board.D2)
#U_MIN         = 200

# Pico RP2040
PIN_CHARGE    = DigitalInOut(board.GP28) # #34
PIN_DISCHARGE = DigitalInOut(board.GP27) # #32
PIN_ADC       = AnalogIn(board.A0)       # #31
U_MIN         = 310

R             = 1000000  # 1MΩ

def init():
  print("initializing...")
  PIN_DISCHARGE.direction = Direction.INPUT
  PIN_CHARGE.direction = Direction.OUTPUT
  PIN_CHARGE.value = 0

def sps():
  print("calculating samples per second")
  start = time.monotonic()
  i = 0
  while i<100:
    i += 1
    PIN_ADC.value
  t2 = time.monotonic() - start
  print("samples per second: {0:7.2f}".format(100/t2))

def discharge():
  print("discharging...")
  PIN_CHARGE.value = 0
  PIN_DISCHARGE.direction = Direction.OUTPUT
  PIN_DISCHARGE.value = 0
  while True:
    u0 = PIN_ADC.value
    print("  {0:5.2f}: {1:5d}".format(time.monotonic(),u0))
    if u0 < U_MIN:
      break
    time.sleep(1)
  PIN_DISCHARGE.direction = Direction.INPUT
  return u0

def meter(u0):
  print("metering...")
  u_tau = 0.6321*65536 + u0
  start = time.monotonic()
  PIN_CHARGE.value = 1
  while True:
    u = PIN_ADC.value
    t = time.monotonic()
    #print("  {0:5.2f}: {1:5d}".format(t,u))
    if u > u_tau:
      # 41425/65536 = 0.6321
      break
  PIN_CHARGE.value = 0
  t2 = t - start
  print("elapsed time: {0:5.4f}".format(t2))
  return t2/R

def print_capacity(c):
  if c < 1e-9:
    size="p"
    c *= 1e+12
  elif c<1e-6:
    size="n"
    c *= 1e+9
  elif c<1e-3:
    size="µ"
    c *= 1e+6
  else:
    size="m"
    c *= 1e+3
  print("capacity: %d%sF" % (int(c),size))

# main program ---

init()
sps()
while True:
  u0 = discharge()
  c = meter(u0)
  print_capacity(c)
  time.sleep(3)
