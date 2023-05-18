# -------------------------------------------------------------------------
# Testprogram for Pimoroni's InkyFrame-5.7"
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

BUILTIN=True

# pylint: disable=no-member

import time
import board
import displayio
import digitalio
import terminalio
import bitmaptools
import busio
import storage
import adafruit_sdcard
import keypad
from adafruit_display_text.bitmap_label import Label
from adafruit_display_shapes.rect import Rect
from digitalio import DigitalInOut, Direction
import gc

LED_TIME = 0.5
TESTS = [
  "show_colors",
  "show_image",
  "blink_leds",
  "use_buttons"
  ]

# pinout for Pimoroni InkyFrame (first group necessary if not builtin)
SCK_PIN   = board.SCLK
MOSI_PIN  = board.MOSI
MISO_PIN  = board.MISO
DC_PIN    = board.INKY_DC
RST_PIN   = board.INKY_RES
CS_PIN_D  = board.INKY_CS

CS_PIN_SD = board.SD_CS
BUSY_PIN  = None
SR_CLOCK  = board.SWITCH_CLK
SR_LATCH  = board.SWITCH_LATCH
SR_DATA   = board.SWITCH_OUT

if BUILTIN:
  display = board.DISPLAY
  spi     = board.SPI()
else:
  import adafruit_spd1656
  displayio.release_displays()
  spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
  display_bus = displayio.FourWire(
    spi, command=DC_PIN, chip_select=CS_PIN_D, reset=RST_PIN, baudrate=1000000
  )
  display = adafruit_spd1656.SPD1656(display_bus,busy_pin=BUSY_PIN,
                                     width=600,height=448,rotation=180,
                                     refresh_time=2)

  display.auto_refresh = False
g = displayio.Group()

pin_led = [board.LED_A, board.LED_B, board.LED_C, board.LED_D, board.LED_E,
           board.LED_ACT, board.LED_CONN
           ]

leds = []
for pin in pin_led:
  led = DigitalInOut(pin)
  led.direction = Direction.OUTPUT
  leds.append(led)

# --- update display   -------------------------------------------------

def update_display():
  start = time.monotonic()
  display.show(g)
  duration = time.monotonic()-start
  print(f"update_display (show): {duration:f}s")

  print("refreshing...: ")
  print(f"time-to-refresh: {display.time_to_refresh}")
  time.sleep(display.time_to_refresh)
  start = time.monotonic()
  display.refresh()
  duration = time.monotonic()-start
  print(f"update_display (refreshed): {duration:f}s")

  update_time = display.time_to_refresh - duration
  if update_time > 0.0:
    print(f"update-time: {update_time}")
    time.sleep(update_time)

  for i in range(len(g)):
    g.pop()

# --- blink all LEDs   -------------------------------------------------

def blink_leds():
  # one LED at a time
  for led in leds:
    led.value = 1
    time.sleep(LED_TIME)
    led.value = 0
    time.sleep(LED_TIME)

  # all LED together
  for led in leds:
    led.value = 1
  time.sleep(LED_TIME)
  for led in leds:
    led.value = 0
  time.sleep(LED_TIME)

# --- colors and texts   -----------------------------------------------

def show_colors():
  p = displayio.Palette(7)
  p[0] = 0xFFFFFF
  p[1] = 0x000000
  p[2] = 0x0000FF
  p[3] = 0x00FF00
  p[4] = 0xFF0000
  p[5] = 0xFFFF00
  p[6] = 0xFFA500

  stripe_height = display.height // 7
  for i in range(7):
    rect = Rect(x=0,y=i*stripe_height,
                width=display.width,height=stripe_height,
                fill=p[i],outline=None,stroke=0)
    g.append(rect)

  lbl = Label(terminalio.FONT, text='InkyFrame 5.7"', color=0xFFFFFF, scale=3)
  lbl.anchor_point = (0.5, 0.5)
  lbl.anchored_position = (display.width // 2, display.height // 2)
  g.append(lbl)
  update_display()

# --- show image from SD   ---------------------------------------------

def show_image():

  cs = digitalio.DigitalInOut(CS_PIN_SD)
  sdcard = adafruit_sdcard.SDCard(spi,cs)
  vfs = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")

  f = open("/sd/display-ruler-600x448.bmp", "rb")
  pic = displayio.OnDiskBitmap(f)
  t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
  g.append(t)
  update_display()
  f.close()

# --- use buttons   -----------------------------------------------------

def use_buttons():

  shift_reg = keypad.ShiftRegisterKeys(
    clock = SR_CLOCK,
    data  = SR_DATA,
    latch = SR_LATCH,
    key_count = 8,
    value_to_latch = True,
    value_when_pressed = True
    )

  queue = shift_reg.events
  queue.clear()
  print("press any button:")
  while True:
    if not len(queue):
      time.sleep(0.1)
      continue
    ev = queue.get()
    if ev.key_number == board.KEYCODES.SW_A:    # only to test board.KEYCODES
      print(f"pressed SW_A")
    key_nr = 7 - ev.key_number                  # bit order reversed compared
    if ev.pressed and key_nr < 5:               # to schematic
      led = leds[key_nr]
      led.value = 1
      time.sleep(LED_TIME)
      led.value = 0
      time.sleep(LED_TIME)

# --- main program   ----------------------------------------------------

for tst in [globals()[fkt] for fkt in TESTS]:
  print(f"running test: {tst}")
  tst()
  gc.collect()
  print(f"finished: {tst}",int(time.monotonic()))
  time.sleep(10)

while True:
  time.sleep(5)
  print("... ",int(time.monotonic()))
