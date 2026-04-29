# SPDX-FileCopyrightText: 2021 Daniel Flanagan
# SPDX-License-Identifier: MIT

import time
import board
import busio
import digitalio
from adafruit_max7219 import matrices

TEXT = "RPG - Geek"
PIN_MOSI = board.GP15
PIN_SCK  = board.GP14
PIN_CS   = board.GP13
DIM_X    = 64
DIM_Y    = 8
SINGLETM = 0.8
SCROLLTM = 0.1

# You may need to change the chip select pin depending on your wiring
spi = busio.SPI(clock=PIN_SCK,MOSI=PIN_MOSI)
cs = digitalio.DigitalInOut(PIN_CS)

matrix = matrices.CustomMatrix(spi, cs, DIM_X, DIM_Y)
while True:
    print("Cycle Start")
    # all lit up
    matrix.fill(True)
    matrix.show()
    time.sleep(0.5)

    # all off
    matrix.fill(False)
    matrix.show()
    time.sleep(0.5)

    # snake across panel
#     for y in range(8):
#         for x in range(DIM_X):
#             if not y % 2:
#                 matrix.pixel(x, y, 1)
#             else:
#                 matrix.pixel(DIM_X - x-1, y, 1)
#             matrix.show()
#             time.sleep(0.05)

    # show a string one character at a time
    matrix.fill(0)
    cut = DIM_X//6
    print("first part:")
    for i, char in enumerate(TEXT[:cut]):
        print(f"{i=}, {char=}")
        matrix.text(char, i * 6, 0)
        matrix.show()
        time.sleep(SINGLETM)

    time.sleep(120)

    print("second part:")
    if cut < len(TEXT):
       matrix.fill(0)
       for i, char in enumerate(TEXT[cut:]):
           print(f"{i=}, {char=}")
           matrix.text(char, i * 6, 0)
           matrix.show()
           time.sleep(SINGLETM)

    # scroll the last character off the display
    print("scroll off:")
    for i in range(min(DIM_X,len(TEXT)*5)):
        matrix.scroll(-1, 0)
        matrix.show()
        time.sleep(SCROLLTM)

    # scroll a string across the display
    print("scroll text:")
    for pixel_position in range(len(TEXT) * 5):
        matrix.fill(0)
        matrix.text(TEXT, -pixel_position, 0)
        matrix.show()
        time.sleep(SCROLLTM)
