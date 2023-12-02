# -------------------------------------------------------------------------
# Run AP together with a web-server.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import board
import socketpool
import wifi

from adafruit_httpserver.mime_types import MIMETypes
from adafruit_httpserver.request import Request
from adafruit_httpserver.response import Response
from adafruit_httpserver.server import Server
from adafruit_httpserver.route import Route
from adafruit_httpserver import GET, POST

# access point settings
from secrets import secrets

#secrets = {
#  'debug' : False,
#  'ssid' : 'my_ssid',
#  'password' : 'my_passwd',            # ignored for wifi.AuthMode.OPEN
#  'auth_modes' : [wifi.AuthMode.OPEN]  # or [wifi.AuthMode.WPA2, wifi.AuthMode.PSK]
#  }

class WebAP:
  """ Access-point and webserver """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- print message in debug-mode   ----------------------------------------

  def msg(self,text):
    if self._config["debug"]:
      print(f"{text}")

  # --- start AP-mode   ------------------------------------------------------

  def start_ap(self):
    """ start in AP-mode """

    wifi.radio.stop_station()

    self.msg(f"starting AP with ssid {self._config['ssid']}")
    if (self._config["auth_modes"][0] == wifi.AuthMode.OPEN):
      wifi.radio.start_ap(ssid=self._config["ssid"],
                          authmode=[wifi.AuthMode.OPEN])
      self.msg("AP is not password-protected!")
    else:
      wifi.radio.start_ap(ssid=self._config["ssid"],
                          password=self._config["password"],
                          authmode=self._config["auth_modes"])
      self.msg(f"password: {self._config['password']}")

  # --- start web-server   ----------------------------------------------------

  def start_ws(self):
    """ start webserver """
    self._pool = socketpool.SocketPool(wifi.radio)
    self._server = Server(self._pool,root_path="/www",
                              debug=self._config["debug"])

    self._server.add_routes([
      Route("/index.html",GET, self._handle_main)
      ])
    self._server.start(str(wifi.radio.ipv4_address_ap))
    self.msg(f"Listening on http://{wifi.radio.ipv4_address_ap}:80")

  # --- poll for requests   --------------------------------------------------

  def poll(self):
    result = self._server.poll()

  # --- request-handler for /index.html   -------------------------------------

  def _handle_main(self,request):
    """ handle request for main-page """
    self.msg("_handle_main...")
    return Response(request, "<h1>Hello from WebAP!</h1>")

# --- main program   ---------------------------------------------------------

server = WebAP(config=secrets)
try:
  server.start_ap()
except Exception as ex:
  print(f"exception: {ex}")
server.start_ws()

while True:
  server.poll()
