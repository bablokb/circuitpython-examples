# -------------------------------------------------------------------------
# main.py: Serve complex index.html with large js/css files
#
# This program needs the ehttpserver module (available via circup).
#
# You need to create a secrets.py file.
#
# Author: Bernhard Bablok
# License: MIT
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

DEBUG  = False

# --- run server   -----------------------------------------------------------

import board
import gc
import wifi
import mdns
import socketpool
import supervisor

from ehttpserver import Server, Response, FileResponse, route

# Get wifi details and more from a secrets.py file
try:
  from secrets import secrets
except ImportError:
  print("WiFi secrets are kept in secrets.py, please add them there!")
  raise

class MyServer(Server):

  # --- request-handler for /   -----------------------------------------------

  @route("/","GET")
  def _handle_main(self,path,query_params, headers, body):
    """ handle request for main-page """
    return FileResponse("/www/index.html")

  # --- request-handler for static files   -----------------------------------

  @route("/[^.]*\.(js|css|html)","GET")
  def _handle_static(self,path,query_params, headers, body):
    """ handle request for static-files """
    return FileResponse(f"/www/{path}",headers={},buffer_size=4096)

  # --- run server   ---------------------------------------------------------

  def run_server(self):

    server = mdns.Server(wifi.radio)
    server.hostname = wifi.radio.hostname
    server.advertise_service(service_type="_http",
                             protocol="_tcp", port=80)
    pool = socketpool.SocketPool(wifi.radio)
    print(f"starting {server.hostname}.local ({wifi.radio.ipv4_address})")
    with pool.socket() as server_socket:
      yield from self.start(server_socket,max_parallel_connections=5)

  # --- run AP and server   --------------------------------------------------

  def run(self):
    """ run server """
    started = False
    for _ in self.run_server():
      if not started:
        print(f"Listening on http://{wifi.radio.ipv4_address}:80")
        started = True
      gc.collect()

# --- connect to AP   --------------------------------------------------------

def connect():
  """ connect to AP with given ssid """

  print(f"connecting to AP {secrets['ssid']} ...")
  if 'timeout' in secrets:
    timeout = secrets['timeout']
  else:
    timeout = 5
  if 'retries' in secrets:
    retries = secrets['retries']
  else:
    retries = 3

  state = wifi.radio.connected
  print(f"  connected: {state}")
  if not state:
    for _ in range(retries):
      try:
        wifi.radio.connect(secrets['ssid'],
                           secrets['password'],
                           timeout = timeout
                           )
        break
      except ConnectionError as ex:
        print(f"{ex}")
    print(f"  connected: {wifi.radio.connected}")

# --- main   ------------------------------------------------------------------

# wait for console to catch all messages
while not supervisor.runtime.serial_connected:
  time.sleep(0.1)
print(f"running on board {board.board_id}")

connect()

myserver = MyServer(debug=True,request_timeout_seconds=30)
myserver.run()
