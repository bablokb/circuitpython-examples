# -------------------------------------------------------------------------
# UDP-datalogging using wifi/socketpool
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import time
import board
import socketpool
import wifi

start_time = time.monotonic()

# Get wifi details and more from a secrets.py file
try:
  from secrets import secrets
except ImportError:
  print("WiFi secrets are kept in secrets.py, please add them there!")
  raise

# try to connect
while True:
  try:
    print("connecting to AP...")
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    break
  except Exception as e:
    print("Failed:\n", e)
    continue

# setup UDP
pool   = socketpool.SocketPool(wifi.radio)
socket = pool.socket(family=socketpool.SocketPool.AF_INET,
                     type=socketpool.SocketPool.SOCK_DGRAM)

# transmit data
print("initialization time: %f\n" % (time.monotonic()-start_time))

while True:
  data = "%6.4f\n" % (1000*time.monotonic())
  data = data.encode('utf-8')
  start = time.monotonic()
  socket.sendto(data,(secrets["remoteip"],secrets["remoteport"]))
  print("tx-time:",time.monotonic()-start)
