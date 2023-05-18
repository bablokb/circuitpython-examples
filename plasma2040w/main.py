# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

from secrets import secrets  # pylint: disable=no-name-in-module

import board
import neopixel
import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer


ssid     = secrets['ssid']
password = secrets['password']
if hasattr(secrets,'ipv4'):
  ipv4    = ipaddress.IPv4Address(secrets['ipv4'])
  netmask = ipaddress.IPv4Address(secrets['netmask'])
  gateway = ipaddress.IPv4Address(secrets['gateway'])
  wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
  print(f"using fixed ip {secrets['ipv4']}")
else:
  print("using dhcp")

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

pixel = neopixel.NeoPixel(board.DATA, 60, bpp=4)
pixel.brightness = 0.1

# --- set brightness   -------------------------------------------------------

@server.route("/brightness/<v>")
def change_brightness_handler(requenst: HTTPRequest):
  """ Change brightness """

  pixel.brightness = int(v or 0)/100
  with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
    response.send(f"Changed brightness to {v}")

# --- set color with path   --------------------------------------------------

@server.route("/color/<r>/<g>/<b>")
def change_neopixel_color_handler_url_params(
  request: HTTPRequest, r: str, g: str, b: str):
  """
  Changes the color of the built-in NeoPixel using URL params.
  """

  pixel.fill((int(r or 0), int(g or 0), int(b or 0)))
  with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
    response.send(f"Changed NeoPixel to color ({r}, {g}, {b})")

print(f"Listening on http://{wifi.radio.ipv4_address}:80")
while True:
  try:
    server.serve_forever(str(wifi.radio.ipv4_address))
  except:
    pass
