# -------------------------------------------------------------------------
# i2c_template/main.py: I2C-template
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/trinket-m0
# Website: https://github.com/bablokb/circuit-python-examples
#
# -------------------------------------------------------------------------

import board
import busio as io
i2c = io.I2C(board.SCL, board.SDA)
