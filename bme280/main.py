import time
import board
import busio
import digitalio
from adafruit_bme280 import advanced as adafruit_bme280

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

while True:
  start = time.monotonic()
  print("{0:f},{1:0.1f},{2:0.1f},{3:0.1f}".format(
    1000*time.monotonic(),
    bme280.temperature,
    (bme280.pressure/alt_fac),
    bme280.humidity))

  time.sleep(10-(time.monotonic()-start))
