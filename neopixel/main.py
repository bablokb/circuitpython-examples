# ----------------------------------------------------------------------------
# Testprogram for Neopixels. Adapted from some neopixel examples from
# Adafruit.
#
# Author: Bernhard Bablok
# License: MIT
#
# Website: https://github.com/bablokb/circuitpython-examples
# ----------------------------------------------------------------------------

import atexit
import time
import board
import neopixel

pixel_pin = board.DATA
num_pixels = 64

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)

def at_exit(pixels):
  """ turn of strip and free ressources """
  print("at_exit(): deinit strip")
  pixels.deinit()

# --- some standard colors   -------------------------------------------------

WHITE = (255,255,255)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

# --- main program   ---------------------------------------------------------

pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                           brightness=0.1, auto_write=False)

atexit.register(at_exit,pixels)

# some idle time (e.g. to measure idle-current)
print("idle for 10 seconds...")
time.sleep(10)
print(f"running with {pixels.n} pixels")

while True:
    print("red...")
    pixels.fill(RED)
    pixels.show()
    # Increase or decrease to change the speed of the solid color change.
    time.sleep(3)
    print("green...")
    pixels.fill(GREEN)
    pixels.show()
    time.sleep(3)
    print("blue...")
    pixels.fill(BLUE)
    pixels.show()
    time.sleep(3)
    print("white...")
    pixels.fill(WHITE)
    pixels.show()
    time.sleep(3)

    print("red...")
    color_chase(RED, 0.1)  # Increase the number to slow down the color chase
    print("yellow...")
    color_chase(YELLOW, 0.1)
    print("green...")
    color_chase(GREEN, 0.1)
    print("cyan...")
    color_chase(CYAN, 0.1)
    print("blue...")
    color_chase(BLUE, 0.1)
    print("purple...")
    color_chase(PURPLE, 0.1)

    print("rainbow...")
    rainbow_cycle(0.2)  # Increase the number to slow down the rainbow
