# -------------------------------------------------------------------------
# Dump memory information
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/trinket-m0
#
# -------------------------------------------------------------------------

import gc

print("free: %s" % gc.mem_free())
