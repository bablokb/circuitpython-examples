# -------------------------------------------------------------------------
# Testprogram for Sunton-ESP32-2432S032C 3.2"-display.
#   - board.DISPLAY (320x240)
#   - button
#   - LED (adafruit_rgbled)
#   - SD-card
#   - backlight
#   - touch
#   - light-sensor
#   - I2C
#   - audio (PWM)
#
# Notes:
#   - light-sensor is not functional (error in hardware-design)
#   - colors-320x240.bmp was created with ImageMagick:
#       convert netscape: -resize '320x240\!' colors-320x240.bmp 
#     copy this file to a SD-card for the "load_image" test
#   - touch coordinates have to be swapped and/or flipped depending on
#     display rotation. Also, a calibration (scaling) makes sense
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

TESTS = [
  #"show_colors",
  #"backlight",
  #"blink_led",
  #"touch",
  # "lightsensor",
  # "aht20",            # test I2C
  #"load_image",
  "audio",
  # "light_sleep_time",
  # "light_sleep_pin",
  # "deep_sleep_time",
  # "deep_sleep_pin",
  ]
SD_FILENAME = "/sd/colors-320x240.bmp"

import board
import time
import gc

import terminalio
import displayio
from digitalio import DigitalInOut, Pull
from adafruit_display_text.bitmap_label import Label
from adafruit_display_shapes.rect import Rect

# --- create global objects   ------------------------------------------------

button = DigitalInOut(board.BUTTON)
button.switch_to_input(pull=Pull.UP)

display = board.DISPLAY
display.auto_refresh = False
main_group = displayio.Group()
display.root_group = main_group
test_group = displayio.Group()
main_group.append(test_group)

tst_name = Label(terminalio.FONT, text=board.board_id, color=0xFFFFFF, scale=2)
tst_name.anchor_point = (0.5, 0.0)
tst_name.anchored_position = (display.width//2,5)
main_group.append(tst_name)
display.refresh()

# --- clear display   --------------------------------------------------------

def clear_display():
  for i in range(len(test_group)):
    test_group.pop()
  gc.collect()

# --- colors and texts (vertical)   ------------------------------------------

def show_colors():
  clear_display()
  N_SHADES = 4
  N_COLORS = N_SHADES*N_SHADES*N_SHADES
  COLOR_STEP = 256/N_SHADES
  stripe_width = display.width // N_COLORS
  i = -1
  for red in range(N_SHADES):
    for green in range(N_SHADES):
      for blue in range(N_SHADES):
        i += 1
        color = ((min(int(COLOR_STEP*red),255) << 16) +
                 (min(int(COLOR_STEP*green),255) << 8) +
                 min(int(COLOR_STEP*blue),255))
        rect = Rect(x=i*stripe_width,y=0,
                width=stripe_width,height=display.height,
                fill=color,outline=None,stroke=0)
        test_group.append(rect)

  lbl = Label(terminalio.FONT, text=board.board_id, color=0xFFFFFF, scale=2)
  lbl.anchor_point = (0.5, 0.5)
  lbl.anchored_position = (display.width//2,display.height//2)
  test_group.append(lbl)
  display.refresh()

# --- backlight test   -------------------------------------------------------

def backlight():
  print("fading out...")
  for b in range(100,-1,-1):
    if not button.value:
      display.brightness = 1.0
      return
    display.brightness = b/100
    if not b%10:
      print(f"{display.brightness=}")
    time.sleep(0.1)

  time.sleep(5)

  print("fading in...")
  for b in range(0,101):
    if not button.value:
      display.brightness = 1.0
      return
    display.brightness = b/100
    if not b%10:
      print(f"{display.brightness=}")
    time.sleep(0.1)

# --- test GT911 touch   -----------------------------------------------------

def touch():
  import gt911
  import busio
  i2c = busio.I2C(sda=board.TOUCH_SDA,scl=board.TOUCH_SCL,frequency=400000)
  gt  = gt911.GT911(i2c)

  while True:
    if not button.value:
      return
    points = gt.touches
    if points:
      for point in points:
        print(point)

# --- blink LED in various colors   ------------------------------------------

def blink_led():
  import adafruit_rgbled
  import adafruit_fancyled.adafruit_fancyled as fancy
  COLORS = [
    ("WHITE",   0xFFFFFF), ("BLACK",   0x000000),
    ("RED",     0xFF0000), ("LIME",    0x00FF00),
    ("BLUE",    0x0000FF), ("YELLOW",  0xFFFF00),
    ("FUCHSIA", 0xFF00FF), ("AQUA",    0x00FFFF),
    ("MAROON",  0x800000), ("GREEN",   0x008000),
    ("NAVY",    0x000080), ("GRAY",    0x808080),
    ("OLIVE",   0x808000), ("TEAL",    0x008080),
    ("PURPLE",  0x800080), ("SILVER",  0xC0C0C0)]

  colors_adj = fancy.gamma_adjust(
    [fancy.unpack(color[1]) for color in COLORS],
    gamma_value=2.2, brightness=0.25)
  with adafruit_rgbled.RGBLED(
    board.LED_RED, board.LED_GREEN, board.LED_BLUE, invert_pwm = True) as led:
    for index, color in enumerate(colors_adj):
      if not button.value:
        break
      color = color.pack()
      print(f"setting LED color to {COLORS[index][0]} {color:#08x}")
      led.color = color
      time.sleep(3)

    print(f"turning LED off")
    led.color = 0x0

# --- test GT911 touch   -----------------------------------------------------

def touch_transform(point):
  if display.rotation == 0:
    return (display.width-point[1],point[0],point[2])
  else:
    # TODO: other rotations
    return point
    
def touch():
  import gt911
  import busio
  i2c = busio.I2C(sda=board.TOUCH_SDA,scl=board.TOUCH_SCL,frequency=400000)
  gt  = gt911.GT911(i2c,i2c_address=0x5D)

  while True:
    if not button.value:
      return
    points = gt.touches
    if points:
      for point in points:
        print(f"orig: {point} -> transform: {touch_transform(point)}")

# --- light-sensor   ---------------------------------------------------------

def lightsensor():
  from analogio import AnalogIn
  adc_light = AnalogIn(board.LDR)

  while True:
    if not button.value:
      return
    light_sum = 0
    for _  in range(3):
      light_sum += adc_light.value
      time.sleep(0.1)
    light = light_sum/3
    print(f"light: {light:0.5f}")
    time.sleep(0.7)

# --- i2-device   ------------------------------------------------------------

def aht20():
  clear_display()
  import adafruit_ahtx0
  aht20 = adafruit_ahtx0.AHTx0(board.I2C())

  lbl = Label(terminalio.FONT, text="", color=0x00FFFF, scale=2)
  lbl.anchor_point = (0.5, 0.5)
  lbl.anchored_position = (display.width//2, display.height//2)
  test_group.append(lbl)

  while True:
    if not button.value:
      return
    t = round(aht20.temperature,1)
    h = round(aht20.relative_humidity,0)
    text = f"{t:0.1f}C  {h:0.0f}%"       # terminalio.FONT has no '°'
    lbl.text = text
    display.refresh()
    print(text)
    time.sleep(5)

# --- load image from SD-card   ----------------------------------------------

def load_image():
  clear_display()
  import os, storage, sdcardio
  try:
    os.mkdir("/sd")
  except:
    pass
  spi    = board.SD_SPI()
  sdcard = sdcardio.SDCard(spi,board.SD_CS,1_000_000)
  vfs    = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")

  img_file = open(SD_FILENAME, "rb")
  bmp  = displayio.OnDiskBitmap(img_file)
  tile = displayio.TileGrid(bmp,pixel_shader=displayio.ColorConverter())

  test_group.append(tile)
  display.refresh()

# --- audio   ----------------------------------------------------------------

def audio():
  """ example-code from Cytron:
  https://www.cytron.io/tutorial/buzzer-unorp2040-circuitpython
  """
  import simpleio

  MELODY_NOTE = [659, 659, 0,   659, 0,    523, 659, 0,    784]
  #             [E5,  E5, REST, E5,  REST, C5,  E5,  REST, G5]
  MELODY_DURATION = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.2]

  while True:
    if not button.value:
      return
    for i in range(len(MELODY_DURATION)):
      if not MELODY_NOTE[i]:
        time.sleep(MELODY_DURATION[i])
      else:
        simpleio.tone(board.SPEAKER,
                      MELODY_NOTE[i],
                      duration=MELODY_DURATION[i])
    time.sleep(0.5)

# --- main program   ---------------------------------------------------------

print(f"Starting tests for {board.board_id}")
print("interrupt a test by pressing the button")
for tst in [(fkt,globals()[fkt]) for fkt in TESTS]:
  time.sleep(3)
  tst_name.text = tst[0]
  display.refresh()
  print(f"running test: {tst[0]}")
  tst[1]()
  print(f"finished: {tst[0]}")

tst_name.text = "finished!"
display.refresh()
print("all tests finished since...")
start = int(time.monotonic())
while True:
  print(f"{int(time.monotonic())-start}s")
  time.sleep(5)
