# -------------------------------------------------------------------------
# Dump memory information
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import time
import gc
time.sleep(5)
print(f"free memory at start: {gc.mem_free()}")
