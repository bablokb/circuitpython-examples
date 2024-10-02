# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
from digitalio import DigitalInOut
import rtc
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager

def query_time():
  response = None
  while True:
    try:
      print(f"Fetching json from {secrets['time_api_url']} ...")
      start = time.monotonic()
      response = wifi.get(secrets['time_api_url'])
      print(f"...done (elapsed time: {time.monotonic()-start}s)")
      break
    except OSError as e:
      print("Failed to get data, retrying\n", e)
      continue
  
  json = response.json()
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

# --- main   -----------------------------------------------------------------

try:
  from secrets import secrets
except ImportError:
  print("WiFi secrets are kept in secrets.py, please add them there!")
  secrets = {
    'ssid' : 'my_ssid',
    'password' : 'my_password',
    'time_api_url': 'http://worldtimeapi.org/api/ip'
  }

print("ESP32 local time")

# pins used py Pimoroni Wireless Pack
spi = busio.SPI(board.GP18, board.GP19, board.GP16)
esp32_cs = DigitalInOut(board.GP7)
esp32_ready = DigitalInOut(board.GP10)
esp32_reset = DigitalInOut(board.GP11)

esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp,secrets,None)
the_rtc = rtc.RTC()

while True:
  query_time()
  print("sleeping for 120s")
  time.sleep(120)                # worldtimeapi.org has rate-limiting
