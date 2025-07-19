#-----------------------------------------------------------------------------
# Test program: time-counter on Waveshare Pico-LCD-0.96
#
# Author: Bernhard Bablok
#
# Website: https://github.com/circuitpython-examples
#-----------------------------------------------------------------------------

import time
import board

import displayio
import fourwire
import busio
from adafruit_st7735r import ST7735R
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

# --- initialization   -------------------------------------------------------

# SPI/TFT pins
PIN_MOSI = board.GP11
PIN_CLK  = board.GP10
PIN_CS   = board.GP9
PIN_DC   = board.GP8
PIN_RST  = board.GP12
PIN_BL   = board.GP13

# TFT-characteristics
TFT_WIDTH  = 160
TFT_HEIGHT =  80
TFT_ROTATE =  90
TFT_BGR    = True

# fonts and colors
FONT      = bitmap_font.load_font("fonts/DejaVuSansMono-Bold-24.bdf")
BG_COLOR  = 0x000000      # black
FG_COLOR  = 0xFF0000      # blue

displayio.release_displays()
spi = busio.SPI(clock=PIN_CLK,MOSI=PIN_MOSI)
bus = fourwire.FourWire(spi,command=PIN_DC,chip_select=PIN_CS,
                         reset=PIN_RST)
display = ST7735R(bus,width=TFT_WIDTH,height=TFT_HEIGHT,
                        colstart=28,rowstart=0,invert=True,
                        rotation=TFT_ROTATE,bgr=TFT_BGR)

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
t_counter = label.Label(FONT,color=FG_COLOR,
                    anchor_point=POS_MAP['C'][0])
t_counter.anchored_position = POS_MAP['C'][1]
group.append(t_counter)
display.root_group = group

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
  counter += 1
  t_counter.text = pp_counter(counter)
  elapsed = time.monotonic() - start
