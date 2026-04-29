# -------------------------------------------------------------------------
# Testprogram for Badger2350 BW e-Paper.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
# -------------------------------------------------------------------------

# pylint: disable=no-member

import time
import board
import displayio

# --- display image   --------------------------------------------------------

def show_image():
  """ show image """

  print("opening image...")
  with open("/display-ruler.bmp", "rb") as f:
    pic = displayio.OnDiskBitmap(f)
    t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
    board.DISPLAY.root_group.append(t)

    print("refreshing display...")
    start = time.monotonic()
    board.DISPLAY.refresh()
    print("...done")
    print("waiting for busy...")
    while board.DISPLAY.busy:
      time.sleep(0.05)
    print(f"...finished after {time.monotonic()-start:0.3f}s")

# --- main program   ---------------------------------------------------------

time.sleep(5)

print(f"buttons turned on at reset: {board.RESET_STATE():#012b}")
if board.ON_RESET_PRESSED(board.SW_A):
  print("SW_A pressed!")
if board.ON_RESET_PRESSED(board.SW_B):
  print("SW_B pressed!")
if board.ON_RESET_PRESSED(board.SW_C):
  print("SW_C pressed!")
if board.ON_RESET_PRESSED(board.SW_DOWN):
  print("SW_DOWN pressed!")
if board.ON_RESET_PRESSED(board.SW_UP):
  print("SW_UP pressed!")
time.sleep(5)

g = displayio.Group()
board.DISPLAY.root_group = g
show_image()

for speed in [board.display.SPEED_SLOW, board.display.SPEED_FAST,
              board.display.SPEED_FASTER, board.display.SPEED_FASTEST]:
  time.sleep(5)
  print(f"changing speed to {speed}...")
  board.display.SET_UPDATE_SPEED(speed)
  show_image()

# --- deep sleep with pimped version of CircuitPython   ----------------------
# low-power patch needed from https://github.com/bablokb/circuitpython-patches

try:
  import alarm
  from digitalio import DigitalInOut, Pull
  # create DIOs: needed to preserve state
  dios = [DigitalInOut(pin) for pin in [
    board.SW_A,board.SW_B,board.SW_C,board.SW_UP,board.SW_DOWN,]]
  for dio in dios:
    dio.pull = Pull.UP
  ta = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+30)
  pa = alarm.pin.PinAlarm(board.SW_INT, value=False, edge=True,
                          pull=True)
  alarm.exit_and_deep_sleep_until_alarms(ta,pa,preserve_dios=dios)
except ImportError:
  # fallback to normal operation
  while True:
    time.sleep(120)
