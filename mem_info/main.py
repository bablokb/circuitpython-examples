# -------------------------------------------------------------------------
# Dump memory information
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import gc
print(f"free memory at start: {gc.mem_free()}")
