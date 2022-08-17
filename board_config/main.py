# -------------------------------------------------------------------------
# Dynamic board configuration example.
#
# For every supported platform, add a file /<board_id>/board_config.py
# and set variables, functions etc. (in this example this is only hello_msg).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import board
import sys

hello_msg = "Hello default message"

try:
  sys.path.insert(0,"./"+board.board_id)
  from board_config import *
except:
  print("no board-specific config-file for %s, using defaults" % board.board_id)
  
print(hello_msg)
