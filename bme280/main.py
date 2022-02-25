import time
import alarm
import board
import busio
import digitalio
from adafruit_bme280 import advanced as adafruit_bme280

# button (with hardware-pullup)
PIN_BTN       = board.GP20
btn           = digitalio.DigitalInOut(PIN_BTN)
btn.direction = digitalio.Direction.INPUT
SLEEP_DEEP    = btn.value

# --- print results   ------------------------------------------------------

def log_data(bme280):
  print("{0:f},{1:0.1f},{2:0.1f},{3:0.1f}".format(
    1000*time.monotonic(),
    bme280.temperature,
    (bme280.pressure/alt_fac),
    bme280.humidity))

# --- loop with light sleep   ----------------------------------------------

def loop():
  while True:
    start = time.monotonic()
    log_data(bme280)

    time_alarm = alarm.time.TimeAlarm(monotonic_time=start+10)
    alarm.light_sleep_until_alarms(time_alarm)

# --- main program   --------------------------------------------------------

start = time.monotonic()

# Create library object using our Bus I2C port
i2c    = busio.I2C(board.GP27, board.GP26)  # SCL, SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c,address=0x76)

bme280.mode                 = adafruit_bme280.MODE_NORMAL
bme280.standby_period       = adafruit_bme280.STANDBY_TC_500
bme280.iir_filter           = adafruit_bme280.IIR_FILTER_X16
bme280.overscan_pressure    = adafruit_bme280.OVERSCAN_X16
bme280.overscan_humidity    = adafruit_bme280.OVERSCAN_X1
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
#bme280.sea_level_pressure  = 996.1
time.sleep(1)

# SPI-version
#spi = busio.SPI(board.SCK,MOSI=board.MOSI,MISO=board.MISO)
#cs  = digitalio.DigitalInOut(board.D5)
#bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi,cs)

altitude_at_location = 525
alt_fac = pow(1.0-altitude_at_location/44330.0, 5.255)

if SLEEP_DEEP:
  log_data(bme280)
  time_alarm = alarm.time.TimeAlarm(monotonic_time=start+10)
  alarm.exit_and_deep_sleep_until_alarms(time_alarm)
else:
  loop()
