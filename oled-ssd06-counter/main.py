#-----------------------------------------------------------------------------
# Test program: time-counter on an OLED
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import time
import board

# output to OLED-display (deep-sleep won't work with usb-serial)
import busio
import displayio
import adafruit_displayio_ssd1306          # I2C-OLED display
OLED_ADDR   = 0x3C
OLED_WIDTH  = 128
OLED_HEIGHT = 64

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

# --- initialization   -------------------------------------------------------

PIN_SDA  = board.GP18
PIN_SCL  = board.GP19
PIN_WAKE = board.GP20

displayio.release_displays()
i2c = busio.I2C(sda=PIN_SDA,scl=PIN_SCL,frequency=400000)
display_bus = displayio.I2CDisplay(i2c, device_address=OLED_ADDR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus,
                                             width=OLED_WIDTH,
                                             height=OLED_HEIGHT)

FONT     = bitmap_font.load_font("fonts/DejaVuSans-Bold-24-min.bdf")
FG_COLOR = 0xFFFFFF
POS_MAP = {
  'NW': ((0.0,0.0),(0,               0)),
  'NE': ((1.0,0.0),(display.width,   0)),
  'W':  ((0.0,0.5),(0,               display.height/2)),
  'C':  ((0.5,0.5),(display.width/2, display.height/2)),
  'E':  ((1.0,0.5),(display.width,   display.height/2)),
  'SW': ((0.0,1.0),(0,               display.height)),
  'SE': ((1.0,1.0),(display.width,   display.height)),
  }

group   = displayio.Group()
t_counter = label.Label(FONT,text='00:00:00',color=FG_COLOR,
                    anchor_point=POS_MAP['C'][0])
t_counter.anchored_position = POS_MAP['C'][1]
group.append(t_counter)

# --- format counter   -------------------------------------------------------

def pp_counter(seconds):
  """ format counter """
  m, s = divmod(seconds,60)
  h, m = divmod(m,60)
  if h > 0:
    return "{0:02d}:{1:02d}:{2:02d}".format(h,m,s)
  else:
    return "{0:02d}:{1:02d}".format(m,s)

# --- main   -----------------------------------------------------------------

counter = 0
start   = time.monotonic()
elapsed = 1
while True:
  time.sleep(max(0,1-elapsed))
  start = time.monotonic()
  display.show(group)
  counter += 1
  t_counter.text = pp_counter(counter)
  elapsed = time.monotonic() - start
