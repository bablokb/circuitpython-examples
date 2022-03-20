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

print("free: %s" % gc.mem_free())
