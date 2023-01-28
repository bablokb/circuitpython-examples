#-----------------------------------------------------------------------------
# Example using the PCF85x3-RTC in timer-mode.
#
# The program uses various timer-features of the PCF8563/PCF8523-RTCs.
#
# The program uses the countdown-timer of the RTC and works on a PCF8563 up to
# 15300 seconds (i.e. 255m or 4h15m). For longer intervals than
# 256 minutes use the alarm-timer or switch to the PCF8523. The latter
# supports up to 255 hours.
#
# On a PCF8523, you can search&replace timerA with timerB to test the
# second timer (the PCF8563 only has a single timer).
#
# Test1: low-frequency timer, checking timer-flag
# Test2: low-frequency timer, checking interrupt-pin
# Test3: high-frequency timer, counting timer-flag
# Test4: high-frequency timer, counting interrupt-pin
# Test5: clock-out, counting rising-edges on clkout-pin
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/circuitpython-examples
#-----------------------------------------------------------------------------

# test to execute
TESTS=[1,2,3,4,5]
REPEAT_LOW=3
REPEAT_HIGH=3

import time
import board
import countio
from digitalio import DigitalInOut, Direction, Pull

# imports for PCF8563
import busio
from adafruit_pcf8523 import PCF8523 as PCF_RTC
#from adafruit_pcf8563 import PCF8563 as PCF_RTC

# --- configuration   --------------------------------------------------------

PIN_INT  = board.GP5   # for PCF8523/PCF8563
PIN_COUT = board.GP5   # for PCF8523
#PIN_COUT = board.GP4   # for PCF8563
PIN_SDA  = board.GP2   # connect to RTC
PIN_SCL  = board.GP3   # connect to RTC

LED_TIME           = 0.5         # blink-duration
DELAY_TIME_LOW     = 10          # delay for timer low-frequency
DELAY_TIME_HIGH    = 0.02        # delay for timer high-frequency
DURATION_TIME_HIGH = 10          # duration of high-frequency tests

CLKOUT_FREQ = PCF_RTC.CLOCKOUT_FREQ_32HZ

FREQ_MAP = {
  PCF_RTC.CLOCKOUT_FREQ_32KHZ: 32768,
  PCF_RTC.CLOCKOUT_FREQ_16KHZ: 16384,
  PCF_RTC.CLOCKOUT_FREQ_8KHZ:   8192,
  PCF_RTC.CLOCKOUT_FREQ_4KHZ:   4096,
  PCF_RTC.CLOCKOUT_FREQ_1KHZ:   1024,
  PCF_RTC.CLOCKOUT_FREQ_32HZ:     32,
  PCF_RTC.CLOCKOUT_FREQ_1HZ:       1
  }

# --- create hardware objects   ----------------------------------------------

led            = DigitalInOut(board.LED)
led.direction  = Direction.OUTPUT

intpin           = DigitalInOut(PIN_INT)
intpin.direction = Direction.INPUT
intpin.pull      = Pull.UP

i2c = busio.I2C(PIN_SCL,PIN_SDA)
rtc = PCF_RTC(i2c)

# --- blink on-board-led   ---------------------------------------------------

def blink(dur=LED_TIME,repeat=1):
  while repeat:
    led.value = 1
    time.sleep(dur)
    led.value = 0
    time.sleep(dur)
    repeat -= 1

# --- get timer-clock and value   --------------------------------------------

def set_timer(delay):
  """set countdown-timer in external RTC to the given delay in seconds"""
  if delay < 0.0000244:
    raise ValueError("delay too small")
  elif delay <= 0.062256:
    rtc.timerA_frequency = rtc.TIMER_FREQ_4KHZ
    rtc.timerA_value = min(round(delay*4096),255)
  elif delay <= 3.984375:
    rtc.timerA_frequency = rtc.TIMER_FREQ_64HZ
    rtc.timerA_value = min(round(delay*64),255)
  elif delay <= 255:
    rtc.timerA_frequency = rtc.TIMER_FREQ_1HZ
    rtc.timerA_value = delay
  elif delay <= 15300:
    rtc.timerA_frequency = rtc.TIMER_FREQ_1_60HZ
    rtc.timerA_value = min(round(delay/60),255)
  elif hasattr(rtc,"lost_power") and delay <= 918000:
    # only supported on PCF8523
    rtc.timerA_frequency = rtc.TIMER_FREQ_1_3600HZ
    rtc.timerA_value = min(round(delay/3600),255)
  else:
    raise ValueError("delay too large")

# --- test 1   ---------------------------------------------------------------

def test1():
  """ Test1: low-frequency timer, checking timer-flag """
  print(f"running test1 (timer flag): delay: {DELAY_TIME_LOW}")
  set_timer(DELAY_TIME_LOW)
  for n in range(REPEAT_LOW):
    start = time.monotonic()
    rtc.timerA_enabled = True
    while not rtc.timerA_status:
      pass
    # timer fired, reset and blink
    rtc.timerA_enabled = False
    rtc.timerA_status  = False
    elapsed = time.monotonic() - start
    print(f"elapsed: {elapsed}")
    blink()

# --- test 2   ---------------------------------------------------------------

def test2():
  """ Test2: low-frequency timer, checking interrupt-pin """
  print(f"running test2 (interrupt): delay: {DELAY_TIME_LOW}")
  set_timer(DELAY_TIME_LOW)
  rtc.timerA_interrupt = True
  for n in range(REPEAT_LOW):
    start = time.monotonic()
    rtc.timerA_enabled   = True
    while intpin.value:
      pass
    # timer fired, reset and blink
    rtc.timerA_enabled   = False
    rtc.timerA_status    = False
    elapsed = time.monotonic() - start
    print(f"elapsed: {elapsed}")
    blink()

# --- test 3   ---------------------------------------------------------------

def test3():
  """ Test3: high-frequency timer, checking timer-flag """
  print(f"running test3 (timer flag): delay: {DELAY_TIME_HIGH}, duration: {DURATION_TIME_HIGH}")
  set_timer(DELAY_TIME_HIGH)
  for n in range(REPEAT_HIGH):             # repeat complete test
    counter = 0
    start = time.monotonic()
    end   = start + DURATION_TIME_HIGH
    rtc.timerA_enabled   = True
    while time.monotonic() < end:          # run for (at least) test-period
      while not rtc.timerA_status:
        pass
      # timer fired: reset and wait for next elapsed timer
      rtc.timerA_status = False
      counter += 1
    mean_delay = (time.monotonic()-start)/counter
    rtc.timerA_enabled = False
    print(f"delay requested: {DELAY_TIME_HIGH}")
    print(f"delay observed:  {mean_delay} (mean of {counter} alarms)")

# --- test 4   ---------------------------------------------------------------

def test4():
  """ Test4: high-frequency timer, counting interrupt-pin """
  print(f"running test4 (interrupt): delay: {DELAY_TIME_HIGH}, duration: {DURATION_TIME_HIGH}")
  set_timer(DELAY_TIME_HIGH)
  rtc.timerA_interrupt = True
  for n in range(REPEAT_HIGH):             # repeat complete test
    counter = 0
    start = time.monotonic()
    end   = start + DURATION_TIME_HIGH
    rtc.timerA_enabled   = True
    while time.monotonic() < end:          # run for (at least) test-period
      while intpin.value:
        pass
      # timer fired: reset and wait for next elapsed timer
      rtc.timerA_status = False
      counter += 1
    mean_delay = (time.monotonic()-start)/counter
    rtc.timerA_enabled = False
    print(f"delay requested: {DELAY_TIME_HIGH}")
    print(f"delay observed:  {mean_delay} (mean of {counter} alarms)")

# --- test 5   ---------------------------------------------------------------

def test5():
  """ Test5: CLKOUT counter (must be last test)"""
  print(f"running test5 (clockout): freq: {FREQ_MAP[CLKOUT_FREQ]}, duration: {DURATION_TIME_HIGH}")

  rtc.timerA_interrupt = False
  intpin.deinit()
  counter = countio.Counter(pin=PIN_COUT,edge=countio.Edge.RISE,
                            pull=Pull.UP)
  for n in range(REPEAT_HIGH):             # repeat complete test
    counter.reset()
    rtc.clockout_frequency = CLKOUT_FREQ
    time.sleep(DURATION_TIME_HIGH)
    rtc.clockout_frequency = rtc.CLOCKOUT_FREQ_DISABLED
    mean_freq = counter.count/DURATION_TIME_HIGH
    print(f"clock-pulses: {counter.count}")
    print(f"clock-freq:   {mean_freq}")

# --- main program   ---------------------------------------------------------

# Check for valid datetime and set a valid, but arbitrary value.
if (hasattr(rtc,"datetime_compromised") and rtc.datetime_compromised or
    hasattr(rtc,"lost_power") and rtc.lost_power):
  print("invalid datetime/power lost: setting to 2023/01/01 12:00:00")
  rtc.datetime = time.struct_time((2023,1,1, 12,0,0, 6,1,-1))

# Configure RTC
rtc.timerA_enabled     = False
rtc.timerA_interrupt   = False
rtc.timerA_status      = False
rtc.timerA_pulsed      = False
rtc.clockout_frequency = rtc.CLOCKOUT_FREQ_DISABLED

# execute tests
for tst in [globals()[f"test{i}"] for i in TESTS]:
  tst()
