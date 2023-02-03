# -------------------------------------------------------------------------
# UDP-datalogging using an ESP-01 as coprocessor.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import time
start_time = time.monotonic()

import board
import busio
from   digitalio import DigitalInOut

from adafruit_espatcontrol import (
  adafruit_espatcontrol,
  adafruit_espatcontrol_wifimanager,
)

# Get wifi details and more from a secrets.py file
try:
  from secrets import secrets
except ImportError:
  print("WiFi secrets are kept in secrets.py, please add them there!")
  raise

PIN_RX  = board.GP1
PIN_TX  = board.GP0
PIN_RST = board.GP2

uart    = busio.UART(PIN_TX, PIN_RX, baudrate=115200, receiver_buffer_size=2048)
rst_pin = DigitalInOut(PIN_RST)

esp = adafruit_espatcontrol.ESP_ATcontrol(
  uart, 115200, reset_pin=rst_pin, rts_pin=None, debug=secrets["debugflag"]
)

wifi = adafruit_espatcontrol_wifimanager.ESPAT_WiFiManager(esp, secrets, None)

# try to connect
while True:
  try:
    print("main: resetting and connecting to AP...")
    wifi.reset()
    wifi.connect(timeout=5,retries=2)
    break
  except Exception as e:
    print("main: failed, retrying: \n", e)
    continue

# setup UDP
while True:
  try:
    print(
      "main: connecting to UDP-server %s:%d" % (secrets["remoteip"],secrets["remoteport"])
    )
    if esp.socket_connect(adafruit_espatcontrol.ESP_ATcontrol.TYPE_UDP,
                          secrets["remoteip"],secrets["remoteport"]):
      break
    else:
      time.sleep(1)
      continue
  except Exception as e:
    print("main: failed:\n", e)
    continue

# transmit data
print("main: initialization time: %f\n" % (time.monotonic()-start_time))
while True:
  data = "%6.4f\n" % (1000*time.monotonic())
  data = data.encode('utf-8')
  start = time.monotonic()
  esp.socket_send(data)
  print("main: tx-time:",time.monotonic()-start)
