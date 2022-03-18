# ----------------------------------------------------------------------------
# fake-data/main.py: simulate datalogging
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuit-python-examples
#
# ----------------------------------------------------------------------------

import time
import alarm
import microcontroller
import random

uid = ''.join('{:02x}'.format(x) for x in microcontroller.cpu.uid)

# --- print results   ------------------------------------------------------

def log_data():
  print("{0:f},{1:s},{2:0.3f},{3:0.3f}".format(
    1000*time.monotonic(),
    uid,
    random.random(),
    random.random()
    ))

# --- main program   --------------------------------------------------------

while True:
  start = time.monotonic()
  log_data()

  time_alarm = alarm.time.TimeAlarm(monotonic_time=start+10)
  alarm.light_sleep_until_alarms(time_alarm)
