# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test script for 2.13" 250x122 monochrome display.

Supported products:
  * Adafruit 2.13" Monochrome ePaper Display Breakout
    * https://www.adafruit.com/product/4197
  """

import time
import board
import displayio
import busio
import adafruit_ssd1675

displayio.release_displays()


epd_cs    = board.GP9
epd_dc    = board.GP8
epd_reset = board.GP7
epd_busy  = board.GP6
epd_sck   = board.GP10
epd_mosi  = board.GP11
spi = busio.SPI(epd_sck,MOSI=epd_mosi)

display_bus = displayio.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
)
time.sleep(1)

display = adafruit_ssd1675.SSD1675(
    display_bus, width=250, height=122, rotation=270, busy_pin=epd_busy
)

g = displayio.Group()

with open("/display-ruler.bmp", "rb") as f:
    pic = displayio.OnDiskBitmap(f)
    # CircuitPython 6 & 7 compatible
    t = displayio.TileGrid(
        pic, pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter())
    )
    # CircuitPython 7 compatible only
    # t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
    g.append(t)

    display.show(g)

    display.refresh()

    print("refreshed")

    time.sleep(120)
