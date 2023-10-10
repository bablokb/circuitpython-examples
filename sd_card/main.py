# -------------------------------------------------------------------------
# Testprogram for sdcard breakout.
#
# This program simulates sensor readouts and writes sensor readings as
# fast as possible to the sdcard. This is a not a typical setup, it is
# just used to find the limits.
#
# There are two test-modes: single and bulk. The former does an open/close
# for every write (robust-version), the second does an open/close every
# BULK_COUNT records (performant version).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

BULK       = False
DURATION   = { False: 30, True: 30 }  # duration depending on BULK
BULK_COUNT = 1000

import time
import adafruit_sdcard
import board
import busio
import digitalio
import microcontroller
import storage

# microSD BFF + XIAO-board
#SD_CS   = board.TX      # default CS pin for the microSD bff is TX
#SD_SCK  = board.SCK
#SD_MOSI = board.MOSI
#SD_MISO = board.MISO

# integrated microSD in pico-pi-base-rev2
#SD_CS   = board.SD_CS
#SD_SCK  = board.SCLK
#SD_MOSI = board.MOSI
#SD_MISO = board.MISO

# pico with SPI1
SD_CS    = board.GP13
SD_SCK   = board.GP14
SD_MOSI  = board.GP15
SD_MISO  = board.GP12

# --- single-logging   ------------------------------------------------------

def run_single():
  i = 1
  start = time.monotonic()
  last  = start
  while time.monotonic() - start < DURATION[BULK]:
    with open("/sd/temperature_single.txt", "a") as f:
      now = time.monotonic()
      data = f"{i},{now-start:.2f},{now-last:.2f},{microcontroller.cpu.temperature}"
      print(data)
      f.write(f"{data}\n")
    last = now
    i += 1
  return i

# --- bulk-logging   ------------------------------------------------------

def run_bulk():
  i = 1
  start = time.monotonic()
  last  = start
  while time.monotonic() - start < DURATION[BULK]:
    with open("/sd/temperature_bulk.txt", "a") as f:
      while True:
        now = time.monotonic()
        data = f"{i},{now-start:.2f},{now-last:.4f},{microcontroller.cpu.temperature}"
        print(data)
        f.write(f"{data}\n")
        last = now
        i += 1
        if i % BULK_COUNT == 1:
          break
  return i

# --- main program   ---------------------------------------------------------

start  = time.monotonic()
spi    = busio.SPI(SD_SCK,SD_MOSI,SD_MISO)
cs     = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(spi,cs)
vfs    = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
print(f"mount:  {time.monotonic()-start:0.3f}s")

if BULK:
  count = run_bulk()
  print(f"bulk:   {DURATION[BULK]/count:0.3f}s")
else:
  count = run_single()
  print(f"single: {DURATION[BULK]/count:0.3f}s")

# results:
#
# - xiaio-rp2040, CP 8.0.5:
#   - single: 0.028 (30/1071)
#   - bulk:   0.003 (30/10000)
#
# - xiaio-nrf52840, CP 8.0.5:
#   - single: 0.027 (30/1115)
#   - bulk:   0.002 (30/14000)
#
# - pico-pi-base, CP 8.1.0-beta2:
#   - single: 0.028 (30/1070)
#   - bulk:   0.003 (30/9000)
