# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""
import board
import time
import gc
import terminalio
import displayio
import fourwire
import busdisplay
import busio

from xpt2046   import XPT2046
from digitalio import DigitalInOut

from adafruit_display_text import label
from adafruit_st7789 import ST7789

# Release any resources currently in use for the displays
displayio.release_displays()

PIN_SPI_CLK  = board.GP10
PIN_SPI_MOSI = board.GP11
PIN_SPI_MISO = board.GP12

PIN_LCD_DC   = board.GP8
PIN_LCD_CS   = board.GP9
PIN_LCD_BL   = board.GP13
PIN_LCD_RST  = board.GP15

PIN_TP_CS  = board.GP16
PIN_TP_IRQ = board.GP17

PIN_SD_CLK = board.GP5
PIN_SD_CMD = board.GP18
PIN_SD_D0  = board.GP19
PIN_SD_D1  = board.GP20
PIN_SD_D2  = board.GP21
PIN_SD_D3  = board.GP22
PIN_SD_CS  = board.GP22

spi = busio.SPI(clock=PIN_SPI_CLK,MOSI=PIN_SPI_MOSI,MISO=PIN_SPI_MISO)
display_bus = fourwire.FourWire(
  spi, command=PIN_LCD_DC, chip_select=PIN_LCD_CS, reset=PIN_LCD_RST,
  baudrate=40_000_000
)

display = ST7789(display_bus,width=320,height=240,rotation=90,
                 rowstart=0,colstart=0,brightness=1.0,
                 backlight_pin=PIN_LCD_BL,backlight_pwm_frequency=100)

touch = XPT2046(spi,DigitalInOut(PIN_TP_CS),
                width=320, height=240,rotation=180)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width,display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(280, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple
inner_sprite = displayio.TileGrid(inner_bitmap,
                                  pixel_shader=inner_palette, x=20, y=20)
splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(scale=3, x=57, y=120)
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

print(f"free memory: {gc.mem_free()}")
time.sleep(3)

# remove existing objects
del text_group[0]
for i in range(len(splash)):
  splash.pop(0)
gc.collect()
print(f"free memory: {gc.mem_free()}")

# add image
with open("/RPG-320x240.bmp", "rb") as f:
  pic = displayio.OnDiskBitmap(f)
  t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
  splash.append(t)
  print(f"free memory: {gc.mem_free()}")

  print("finished!")
  print("press CTRL-C")
  while True:
    touch.update()
    if touch.coordinate is not None:
      print(f"touch detected at: {touch.coordinate}")
    time.sleep(0.1)
