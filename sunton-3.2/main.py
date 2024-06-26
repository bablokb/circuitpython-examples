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
#   - full brightness: 150mA
#   - light-sleep (timer): 67mA
#   - deep-sleep (timer): 21mA@5V, 36mA@3.6V
#     The LiPo-charger chip cuts power after 32s below 45mA, so deep-sleep
#     is not usable when running from battery
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

TESTS = [
  "show_colors",
  "backlight",
  "blink_led",
  "touch",
  "lightsensor",
  "aht20",            # test I2C
  "load_image",
  "audio",
  "light_sleep_time",
  "deep_sleep_time",
  ]
SD_FILENAME = "/sd/colors-320x240.bmp"
SLEEP_TIME = 60

import board
import time
import gc
import alarm

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

# --- check for button until timer expires   ---------------------------------

def check_button(duration):
  start = time.monotonic()
  while time.monotonic() - start < duration:
    if not button.value:
      return True
  return False

# --- colors and texts (vertical)   ------------------------------------------

def show_colors():
  start = time.monotonic()
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
  start = elapsed_time(start,"show_colors (ui)")
  display.refresh()
  start = elapsed_time(start,"show_colors (refresh)")

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
      color = color.pack()
      print(f"setting LED color to {COLORS[index][0]} {color:#08x}")
      led.color = color
      if check_button(3):
        break

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
    light_sum = 0
    for _  in range(3):
      light_sum += adc_light.value
      time.sleep(0.1)
    light = light_sum/3
    print(f"light: {light:0.5f}")
    if check_button(1):
      return

# --- i2-device   ------------------------------------------------------------

def aht20():
  clear_display()
  import adafruit_ahtx0

  lbl = Label(terminalio.FONT, text="", color=0x00FFFF, scale=2)
  lbl.anchor_point = (0.5, 0.5)
  lbl.anchored_position = (display.width//2, display.height//2)
  test_group.append(lbl)

  try:
    aht20 = adafruit_ahtx0.AHTx0(board.I2C())
  except Exception as ex:
    lbl.text = f"{ex}"
    display.refresh()
    return

  while True:
    t = round(aht20.temperature,1)
    h = round(aht20.relative_humidity,0)
    text = f"{t:0.1f}C  {h:0.0f}%"       # terminalio.FONT has no '°'
    lbl.text = text
    display.refresh()
    print(text)
    if check_button(5):
      return

# --- load image from SD-card   ----------------------------------------------

def load_image():
  start = time.monotonic()
  clear_display()
  import os, storage, sdcardio
  try:
    os.mkdir("/sd")
  except:
    pass
  try:
    spi    = board.SD_SPI()
    sdcard = sdcardio.SDCard(spi,board.SD_CS,1_000_000)
    vfs    = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    img_filename = SD_FILEANAME
  except:
    img_filename = SD_FILENAME.split('/')[2]

  img_file = open(img_filename, "rb")
  bmp  = displayio.OnDiskBitmap(img_file)
  tile = displayio.TileGrid(bmp,pixel_shader=displayio.ColorConverter())

  test_group.append(tile)
  start = elapsed_time(start,"load_image (load)")
  display.refresh()
  start = elapsed_time(start,"load_image (refresh)")

# --- audio   ----------------------------------------------------------------

def audio():
  """ code adapted from:
  https://blog.wokwi.com/play-musical-notes-on-circuitpython/
  """
  import simpleio
  PITCHES = "c,c#,d,d#,e,f,f#,g,g#,a,a#,b".split(",")
  def get_freq(name):
    octave = int(name[-1])
    pitch = PITCHES.index(name[:-1].lower())
    return 440 * 2 ** ((octave - 4) + (pitch - 9) / 12.)

  def play_jingle():
    sequence = [
      ("e5", 2), ("e5", 2), ("e5", 4), ("e5", 2), ("e5", 2), ("e5", 4),
      ("e5", 2), ("g5", 2), ("c5", 4), ("d5", 1), ("e5", 6), (None, 2),
      ("f5", 2), ("f5", 2), ("f5", 3), ("f5", 1), ("f5", 2), ("e5", 2),
      ("e5", 2), ("e5", 1), ("e5", 1), ("e5", 2), ("d5", 2), ("d5", 2),
      ("e5", 2), ("d5", 4), ("g5", 2), (None, 2),
      ("e5", 2), ("e5", 2), ("e5", 4), ("e5", 2), ("e5", 2), ("e5", 4),
      ("e5", 2), ("g5", 2), ("c5", 4), ("d5", 1), ("e5", 6), (None, 2),
      ("f5", 2), ("f5", 2), ("f5", 3), ("f5", 1), ("f5", 2), ("e5", 2),
      ("e5", 2), ("e5", 1), ("e5", 1), ("g5", 2), ("g5", 2), ("f5", 2),
      ("d5", 2), ("c5", 6), (None, 2)
      ]

    for (notename, eigths) in sequence:
      if not button.value:
        return True
      length = eigths * 0.1
      if notename:
        simpleio.tone(board.SPEAKER,get_freq(notename),length)
      else:
        time.sleep(length)
    return False

  while True:
    if play_jingle():
      return
    if check_button(1):
      return

# --- light-sleep until timer expires   --------------------------------------

def light_sleep_time():
  while True:
    if check_button(5):
      return
    print("turning display off")
    old_brightness = display.brightness
    display.brightness = 0
    print(f"sleeping for {SLEEP_TIME} seconds")
    time_alarm = alarm.time.TimeAlarm(
      monotonic_time=time.monotonic() + SLEEP_TIME)
    alarm.light_sleep_until_alarms(time_alarm)
    print(f"continue after wakeup!")
    display.brightness = old_brightness

# --- deep-sleep until timer expires   --------------------------------------

def deep_sleep_time():
  while True:
    if check_button(5):
      return
    #print("turning display off")
    #old_brightness = display.brightness
    #display.brightness = 0
    print(f"sleeping for {SLEEP_TIME} seconds")
    time_alarm = alarm.time.TimeAlarm(
      monotonic_time=time.monotonic() + SLEEP_TIME)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

# --- print elapsed time   ---------------------------------------------------

def elapsed_time(start,text):
  print(f"{text}: {time.monotonic()-start}")
  return time.monotonic()

# --- main program   ---------------------------------------------------------

print(f"Starting tests for {board.board_id}")
print("interrupt a test by pressing the button")
start = time.monotonic()
for tst in [(fkt,globals()[fkt]) for fkt in TESTS]:
  time.sleep(3)
  start = elapsed_time(start,f"{tst[0]} (sleep)")
  tst_name.text = tst[0]
  display.refresh()
  start = elapsed_time(start,f"{tst[0]} (title)")
  print(f"running test: {tst[0]}")
  tst[1]()
  start = elapsed_time(start,f"{tst[0]} (run)")
  print(f"finished: {tst[0]}")

tst_name.text = "finished!"
display.refresh()
print("all tests finished since...")
start = int(time.monotonic())
while True:
  print(f"{int(time.monotonic())-start}s")
  time.sleep(5)
