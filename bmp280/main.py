import time
import alarm
import board
import busio
import digitalio
import adafruit_bmp280

# button (with hardware-pullup)
PIN_BTN       = board.GP20
btn           = digitalio.DigitalInOut(PIN_BTN)
btn.direction = digitalio.Direction.INPUT
SLEEP_DEEP    = btn.value

SLEEP_DEEP = False

# --- print results   ------------------------------------------------------

def log_data(bmp280):
  print("{0:f},{1:0.1f},{2:.0f}".format(
    1000*time.monotonic(),
    bmp280.temperature,
    (bmp280.pressure/alt_fac)))

# --- loop with light sleep   ----------------------------------------------

def loop():
  while True:
    start = time.monotonic()
    bmp280.mode = adafruit_bmp280.MODE_FORCE
    log_data(bmp280)

    time_alarm = alarm.time.TimeAlarm(monotonic_time=start+10)
    alarm.light_sleep_until_alarms(time_alarm)

# --- main program   --------------------------------------------------------

start = time.monotonic()
time.sleep(0.05)

# Create library object using our Bus I2C port
i2c    = busio.I2C(board.GP27, board.GP26)  # SCL, SDA
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# recommended settings: datasheet 3.5.1 weather monitoring

#bmp280.standby_period       = adafruit_bmp280.STANDBY_TC_500  # for MODE_NORMAL
bmp280.iir_filter           = adafruit_bmp280.IIR_FILTER_DISABLE
bmp280.overscan_pressure    = adafruit_bmp280.OVERSCAN_X1
bmp280.overscan_temperature = adafruit_bmp280.OVERSCAN_X1
#bmp280.sea_level_pressure  = 996.1

altitude_at_location = 525
alt_fac = pow(1.0-altitude_at_location/44330.0, 5.255)

if SLEEP_DEEP:
  log_data(bmp280)
  time_alarm = alarm.time.TimeAlarm(monotonic_time=start+10)
  alarm.exit_and_deep_sleep_until_alarms(time_alarm)
else:
  loop()
