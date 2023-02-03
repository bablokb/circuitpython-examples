# -------------------------------------------------------------------------
# Update on-chip RTC using an ESP-01 as coprocessor.
#
# Adapted from sample esp_atcontrol_localtime.py for the pico.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import rtc

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

# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = False

# How Long to sleep between polling
sleep_duration = 10

PIN_RX = board.GP1
PIN_TX = board.GP0
uart = busio.UART(PIN_TX, PIN_RX, baudrate=11520, receiver_buffer_size=2048)
status_light = None

esp = adafruit_espatcontrol.ESP_ATcontrol(
  uart, 115200, reset_pin=None, rts_pin=None, debug=debugflag
)
wifi = adafruit_espatcontrol_wifimanager.ESPAT_WiFiManager(
  esp, secrets, status_light
)

# try to connect
try:
  print("trying to connect...",end='')
  wifi.connect()
  print("...done")
except Exception as e:
  print("...failed: %r" % e)
  raise e
  #raise RuntimeError("failed to connect to %s" % secrets['ssid'])

TIME_API = secrets["time_api_url"]
the_rtc = rtc.RTC()

response = None
while True:
  try:
    print("Fetching json from", TIME_API)
    response = wifi.get(TIME_API)
    break
  except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
    print("Failed to get data, retrying\n", e)
    continue

json = response.json()
if 'struct_time' in json:
  now = time.struct_time(tuple(json['struct_time']))
else:
  current_time = json["datetime"]
  the_date, the_time = current_time.split("T")
  year, month, mday = [int(x) for x in the_date.split("-")]
  the_time = the_time.split(".")[0]
  hours, minutes, seconds = [int(x) for x in the_time.split(":")]

  # We can also fill in these extra nice things
  year_day = json["day_of_year"]
  week_day = json["day_of_week"]
  is_dst = json["dst"]

  now = time.struct_time(
    (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
  )

print(now)
the_rtc.datetime = now

while True:
  print(time.localtime())
  print("Sleeping for: {0} Seconds".format(sleep_duration))
  time.sleep(sleep_duration)
