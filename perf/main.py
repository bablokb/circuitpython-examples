# -------------------------------------------------------------------------
# Run a number of performance tests.
#
# The individual tests are a random choice from the CircuitPython repository,
# subdirectory tests/basics and tests/perf_bench.
#
# To run the tests, add a SD-breakout and update the pins. Note that none
# of the tests actually write to the SD-card, it is just mounted.
#
# Website: https://github.com/bablokb/circuitpython-examples
# -------------------------------------------------------------------------

import atexit
import board
import busio
import gc
import sdcardio
import storage
import time

# pico
SD_CS    = board.GP17
SD_SCK   = board.GP18
SD_MOSI  = board.GP19
SD_MISO  = board.GP16

def at_exit(spi):
  """ release spi """
  print(f"releasing {spi}")
  spi.deinit()

def mount_sd():
  try:
    spi    = busio.SPI(SD_SCK,SD_MOSI,SD_MISO)
    sdcard = sdcardio.SDCard(spi,SD_CS,1_000_000)
    vfs    = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    print("SD-card mounted on /sd")
    atexit.register(at_exit,spi)
  except Exception as ex:
    if spi:
      spi.deinit()
    raise

time.sleep(5)
mount_sd()

gc.collect()
print("starting chaos")
import chaos

gc.collect()
print("starting pidigits")
import pidigits

gc.collect()
print("starting wordcount")
import wordcount

gc.collect()
print("starting dict_copy")
import dict_copy

gc.collect()
print("starting list_sort")
import list_sort

# CP 9.2.9
# starting chaos
# 205536 50 1
# starting pidigits
# 192413 65 31415926535897932384626433832795028841971693993751058209749445923
# starting wordcount
# 299102 8 (8, 80, 64)
# starting dict_copy
# 1000
# elapsed: 33264
# starting list_sort
# 0 1999
# 1999 0
# elapsed: 2940704

# CP 10.1.0-beta1+
# starting chaos
# 3484559 50 1
# starting pidigits
# 2263458 65 31415926535897932384626433832795028841971693993751058209749445923
# starting wordcount
# 2572388 8 (8, 80, 64)
# starting dict_copy
# 1000
# elapsed: 324524
# starting list_sort
# 0 1999
# 1999 0
# elapsed: 3074005
