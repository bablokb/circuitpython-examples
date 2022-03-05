import board
import displayio
import framebufferio
import sharpdisplay
import busio

from adafruit_display_text.label import Label
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

label = Label(font=FONT,
              text="BLACK\nLIVES\nMATTER",
              x=120,y=50,
              scale=4,
              line_spacing=1.2)

display.show(label)

while True:
  pass
