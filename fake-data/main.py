# ----------------------------------------------------------------------------
# fake-data/main.py: simulate datalogging
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuit-python-examples
#
# ----------------------------------------------------------------------------

import board
import time
import alarm
import microcontroller
import random
import busio

uart = busio.UART(board.GP0, board.GP1, baudrate=115200)
uid  = ''.join('{:02x}'.format(x) for x in microcontroller.cpu.uid)

# --- print results   ------------------------------------------------------

def log_data():
  uart.write(bytearray("{0:f},{1:s},{2:0.3f},{3:0.3f}\r\n".format(
    1000*time.monotonic(),
    uid,
    random.random(),
    random.random()
    ).encode()))

# --- main program   --------------------------------------------------------

while True:
  start = time.monotonic()
  log_data()

  time_alarm = alarm.time.TimeAlarm(monotonic_time=start+10)
  alarm.light_sleep_until_alarms(time_alarm)
