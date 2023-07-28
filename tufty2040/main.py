import board
import gc
import displayio
import time

from adafruit_display_text.label import Label
from adafruit_display_shapes.circle import Circle
from terminalio import FONT

# --- main program   -----------------------------------------------------

BLACK = 0x000000
WHITE = 0xFFFFFF        # will fail
WHITE = 0xEEEEEE        # works

FG = BLACK
BG = WHITE

display = board.DISPLAY

# Make the display context
main_group = displayio.Group()

# Make a background color fill
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BG
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(bg_sprite)

# Setting up the Circle starting position
posx = 50
posy = 50

# Define Circle characteristics
circle_radius = 20
circle = Circle(posx, posy, circle_radius, fill=FG, outline=0)
main_group.append(circle)

# Define Circle Animation Steps
delta_x = 2
delta_y = 2

display.root_group = main_group

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

  time.sleep(0.02)
  gc.collect()
