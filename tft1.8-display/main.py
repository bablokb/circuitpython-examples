# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw 8 colored
labels. Useful for testing the color settings on an unknown display.
"""

import board
import busio
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_st7735r import ST7735R

# Release any resources currently in use for the displays
displayio.release_displays()

#spi = board.SPI()

PIN_CLK = board.GP14
PIN_RX  = board.GP16    # unused
PIN_TX  = board.GP15
PIN_CS  = board.GP9
PIN_DC  = board.GP10
PIN_RST = board.GP11

WIDTH  = 160
HEIGHT = 128

spi = busio.SPI(clock=PIN_CLK,MOSI=PIN_TX)       #, MISO=PIN_RX)

display_bus = displayio.FourWire(
    spi, command=PIN_DC, chip_select=PIN_CS, reset=PIN_RST
)

display = ST7735R(
    display_bus, width=WIDTH, height=HEIGHT, rotation=270, bgr=True
)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
# write some text in each font color, rgb, cmyk
color_palette[0] = 0xBBBBBB  # light grey

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

text_group_left = displayio.Group(scale=1, x=0, y=6)
text_area_red = label.Label(terminalio.FONT, text="RED", color=0xFF0000)
text_area_green = label.Label(terminalio.FONT, text="\nGREEN", color=0x00FF00)
text_area_blue = label.Label(terminalio.FONT, text="\n\nBLUE", color=0x0000FF)
text_area_white = label.Label(terminalio.FONT, text="\n\n\nWHITE", color=0xFFFFFF)
text_group_left.append(text_area_red)
text_group_left.append(text_area_green)
text_group_left.append(text_area_blue)
text_group_left.append(text_area_white)
splash.append(text_group_left)

text_group_right = displayio.Group(scale=1, x=80, y=6)
text_area_cyan = label.Label(terminalio.FONT, text="CYAN", color=0x00FFFF)
text_group_right.append(text_area_cyan)
text_area_magenta = label.Label(terminalio.FONT, text="\nMAGENTA", color=0xFF00FF)
text_group_right.append(text_area_magenta)
text_area_yellow = label.Label(terminalio.FONT, text="\n\nYELLOW", color=0xFFFF00)
text_group_right.append(text_area_yellow)
text_area_black = label.Label(terminalio.FONT, text="\n\n\nBLACK", color=0x000000)
text_group_right.append(text_area_black)
splash.append(text_group_right)

while True:
    pass
