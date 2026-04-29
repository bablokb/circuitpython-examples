#-----------------------------------------------------------------------------
# Sensor definition for SCD4X.
#
# Naming convention:
#   - filenames in lowercase (scd4x.py)
#   - class name the same as filename in uppercase (SCD4X)
#   - the constructor must take five arguments (config,i2c0,ic1,spi0,spi1)
#     and probe for the device
#   - i2c1 is the default i2c-device and should be probed first
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

SAMPLES = 4
DISCARD = False                # only keep last reading

#from log_writer import Logger
#g_logger = Logger()

class Logger:
  def print(self,msg):
    print(msg)
g_logger = Logger()

import time
import adafruit_scd4x

class SCD4X:
  # we don't show timestamps on the display ...
  formats = ["CO2:", "{0}"]
  if DISCARD:
    # ... and when we don't test readings
    headers = 'CO2 ppm'
  else:
    headers = 't (1),CO2 ppm (1)'
    for i in range(SAMPLES):
      headers += f",t ({i+1}),CO2 ppm ({i+1})"

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.scd4x = None
    for bus,nr in i2c:
      try:
        g_logger.print(f"testing scd4x on i2c{nr}")
        self.scd4x = adafruit_scd4x.SCD4X(bus)
        g_logger.print(f"detected scd4x on i2c{nr}")
        self.scd4x.start_periodic_measurement()
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.scd4x:
      raise Exception("no scd4x detected. Check config/cabling!")

  def read(self,data,values):
    # take multiple readings
    csv_results = ""
    t0 = time.monotonic()
    for i in range(SAMPLES):
      g_logger.print("scd4x: waiting for data...")
      while True:
        if self.scd4x.data_ready:
          t_rel = time.monotonic() - t0
          co2   = self.scd4x.CO2
          g_logger.print(f"scd4x: CO2 at {t_rel:.2f}: {co2}")
          if not DISCARD:
            csv_results += f",{t_rel:.2f},{co2}"
          break
        else:
          time.sleep(0.2)

    if DISCARD:
      # keep last reading
      csv_results = f",{co2}"
    # only show last reading on display
    data["scd4x"] = co2
    values.extend([None,co2])
    return csv_results[1:]
