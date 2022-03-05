import board
import gc
import displayio
import framebufferio
import sharpdisplay
import busio
import time

from adafruit_display_text.label import Label
from adafruit_display_shapes.circle import Circle
from terminalio import FONT

displayio.release_displays()

# --- SPI configuration   ------------------------------------------------

PIN_CLK = board.GP18
PIN_RX  = board.GP16    # unused
PIN_TX  = board.GP19
PIN_CS  = board.GP17
bus = busio.SPI(clock=PIN_CLK,MOSI=PIN_TX)       #, MISO=PIN_RX)

# --- display configuration   --------------------------------------------

WIDTH  = 400
HEIGHT = 240

# --- main program   -----------------------------------------------------

# For the 400x240 display (can only be operated at 2MHz)
framebuffer = sharpdisplay.SharpMemoryFramebuffer(bus,PIN_CS,WIDTH,HEIGHT)
display     = framebufferio.FramebufferDisplay(framebuffer)

# Make the display context
main_group = displayio.Group()

# Make a background color fill
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(bg_sprite)

# label = Label(font=FONT,
#               text="BLACK\nLIVES\nMATTER",
#               x=120,y=50,
#               scale=4,
#               line_spacing=1.2,color=0)
# main_group.append(label)

# Setting up the Circle starting position
posx = 50
posy = 50

# Define Circle characteristics
circle_radius = 20
circle = Circle(posx, posy, circle_radius, fill=0xFFFFFF, outline=0)
main_group.append(circle)

# Define Circle Animation Steps
delta_x = 2
delta_y = 2

display.show(main_group)

while True:
  if circle.y + circle_radius >= display.height - circle_radius:
    delta_y = -1
  if circle.x + circle_radius >= display.width - circle_radius:
    delta_x = -1
  if circle.x - circle_radius <= 0 - circle_radius:
    delta_x = 1
  if circle.y - circle_radius <= 0 - circle_radius:
    delta_y = 1

  circle.x = circle.x + delta_x
  circle.y = circle.y + delta_y

  time.sleep(0.01)
  gc.collect()
