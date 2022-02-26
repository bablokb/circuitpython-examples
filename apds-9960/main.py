import time
import alarm
import board
import busio
import digitalio
import pwmio
from adafruit_apds9960.apds9960 import APDS9960


# --- beep   --------------------------------------------------------------

def beep():
  buzzer.duty_cycle = 65535 // 16
  time.sleep(0.1)
  buzzer.duty_cycle = 0

buzzer = pwmio.PWMOut(board.GP18,frequency=880,duty_cycle=0)
i2c    = busio.I2C(board.GP27, board.GP26)  # SCL, SDA

apds = APDS9960(i2c)
apds._write8(0x8F,13)                          # set PGAIN=3, i.e. 8x
apds.proximity_interrupt_threshold = (0,5,5)
apds.enable_proximity_interrupt = True

# enable the sensor's proximity engine
apds.enable_proximity = True
#apds.enable_gesture   = True

beep()
while True:
  pin_alarm = alarm.pin.PinAlarm(board.GP13,value=False,edge=True,pull=True)
  alarm.light_sleep_until_alarms(pin_alarm)
  print(apds.proximity)
  beep()
  apds.clear_interrupt()

  # print the proximity reading when the interrupt pin goes low
#   if not int_pin.value:
#     print(apds.proximity)
  
    # clear the interrupt
#    apds.clear_interrupt()

#  gesture = apds.gesture()

#   if gesture == 0x01:
#     print("up")
#   elif gesture == 0x02:
#     print("down")
#   elif gesture == 0x03:
#     print("left")
#   elif gesture == 0x04:
#     print("right")
