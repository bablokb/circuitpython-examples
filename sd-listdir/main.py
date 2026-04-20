# -------------------------------------------------------------------------
# Testprogram for sdcard.
#
# This program just mounts the sd-card and lists the content.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
# -------------------------------------------------------------------------

import board
import busio
import os
import sdcardio
import storage
import time

# --- main loop   ------------------------------------------------------------

# give time to the console
time.sleep(5)

# SD-card
SD_MOSI = board.GP19
SD_SCK  = board.GP18
SD_MISO = board.GP16
SD_CS   = board.GP17
spi0 = busio.SPI(SD_SCK,SD_MOSI,SD_MISO)
sdcard = sdcardio.SDCard(spi0,SD_CS)
vfs    = storage.VfsFat(sdcard)
print("mounting /sd")
storage.mount(vfs, "/sd")

print("content of /sd:")
for item in os.listdir("/sd"):
  print(  f"{item}")

print("looping...")
while True:
  pass
