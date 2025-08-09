import time
import board
import busio
import digitalio
from adafruit_bme280 import advanced as adafruit_bme280

# configuration
INTERVAL = 10
ALTITUDE_AT_LOCATION = 525
SLEEP = "LIGHT"                  # None, LIGHT, DEEP

# I2C-pins
SDA = getattr(board,"SDA",board.GP0)
SCL = getattr(board,"SCL",board.GP1)

try:
  import alarm
except:
  SLEEP = None

# --- print results   ------------------------------------------------------

def log_data(bme280,start):
  print("{0:0.1f},{1:0.1f},{2:0.0f},{3:0.0f}".format(
    time.monotonic()-start,
    round(bme280.temperature,1),
    round(bme280.pressure/alt_fac,0),
    round(bme280.humidity,0)))

# --- loop   ---------------------------------------------------------------

def loop():
  while True:
    log_data(bme280,start)

    if SLEEP:
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+INTERVAL)
      alarm.light_sleep_until_alarms(time_alarm)
    else:
      time.sleep(INTERVAL)

# --- main program   --------------------------------------------------------

start = time.monotonic()
time.sleep(0.05)

# Create library object using our Bus I2C port
i2c    = busio.I2C(SCL, SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c,address=0x76)

# recommended settings: datasheet 3.5.1 weather monitoring

bme280.mode                 = adafruit_bme280.MODE_FORCE
#bme280.standby_period       = adafruit_bme280.STANDBY_TC_500  # for MODE_NORMAL
bme280.iir_filter           = adafruit_bme280.IIR_FILTER_DISABLE
bme280.overscan_pressure    = adafruit_bme280.OVERSCAN_X1
bme280.overscan_humidity    = adafruit_bme280.OVERSCAN_X1
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X1
#bme280.sea_level_pressure  = 996.1

# SPI-version
#spi = busio.SPI(board.SCK,MOSI=board.MOSI,MISO=board.MISO)
#cs  = digitalio.DigitalInOut(board.D5)
#bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi,cs)

alt_fac = pow(1.0-ALTITUDE_AT_LOCATION/44330.0, 5.255)

start = time.monotonic()
if SLEEP == "DEEP":
  log_data(bme280,start)
  time_alarm = alarm.time.TimeAlarm(monotonic_time=start+INTERVAL)
  alarm.exit_and_deep_sleep_until_alarms(time_alarm)
else:
  loop()
