#-----------------------------------------------------------------------------
# Example using the PCF85x3-RTC in timer-mode.
#
# The program uses various timer-features of the PCF8563/PCF85063/PCF8523-RTCs.
#
# The program uses the countdown-timer of the RTC and works on a PCF8563 up to
# 15300 seconds (i.e. 255m or 4h15m). For longer intervals than
# 256 minutes use the alarm-timer or switch to the PCF8523. The latter
# supports up to 255 hours.
#
# On a PCF8523, you can search&replace timerA with timerB to test the
# second timer (the PCF8563 only has a single timer).
#
# Test0: check alarm-flag 
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

import time
import board
import countio
from digitalio import DigitalInOut, Direction, Pull
import busio

# imports for PCF8523
from adafruit_pcf8523.pcf8523 import PCF8523 as PCF_RTC
from adafruit_pcf8563.timer import Timer
from adafruit_pcf8563.clock import Clock

# imports for PCF8563
#from adafruit_pcf8563.pcf8563 import PCF8563 as PCF_RTC
#from adafruit_pcf8563.timer import Timer
#from adafruit_pcf8563.clock import Clock

# imports for PCF85063A
#from pcf85063a import PCF85063A as PCF_RTC

# --- configuration   --------------------------------------------------------

# pico left side
PIN_SDA  = board.GP2   # connect to RTC
PIN_SCL  = board.GP3   # connect to RTC
PIN_INT  = board.GP5   # for PCF8523/PCF8563
#PIN_COUT = board.GP7   # for PCF8563
PIN_COUT = board.GP5   # for PCF8523

# pico right side
#PIN_SDA  = board.GP26   # connect to RTC
#PIN_SCL  = board.GP27   # connect to RTC
#PIN_INT  = board.GP22   # for PCF8523/PCF8563
#PIN_COUT = board.GP21   # for PCF8563
#PIN_COUT = board.GP22   # for PCF8523

INT_ACT  = 0           # interrupt is active-low
TESTS=[0,1,2,3,4,5]    # pico
TESTS=[1]              # pico

#Probleme: 1: passiert nichts
#Probleme: 2: falsche Zeiten: 0.001 statt 10
#Probleme: 3: passiert nichts
#Probleme: 4: falsche Zeiten: 0.001 statt 0.02

# XIAO RP2040 with expansion board and RTC8563
#PIN_SDA  = board.SDA   # connect to RTC
#PIN_SCL  = board.SCL   # connect to RTC
#PIN_INT  = None
#INT_ACT  = 0           # interrupt is active-low
#PIN_COUT = None
#TESTS=[1,3]           # XIAO RP2040 with expansion board and RTC8563

# Badger2040W with PCF85063A
#PIN_SDA  = board.SDA
#PIN_SCL  = board.SCL
#PIN_INT  = board.RTC_ALARM
#INT_ACT  = 1           # interrupt is active-high
#PIN_COUT = None
#TESTS=[1,2,3,4]

REPEAT_LOW=3
REPEAT_HIGH=3

LED_TIME           = 0.5         # blink-duration
DELAY_TIME_LOW     = 10          # delay for timer low-frequency
DELAY_TIME_HIGH    = 0.02        # delay for timer high-frequency
DURATION_TIME_HIGH = 10          # duration of high-frequency tests
ALARM_TIME         = 65          # alarm in now + xx secs

CLKOUT_FREQ = Clock.CLOCKOUT_FREQ_32KHZ

# --- create hardware objects   ----------------------------------------------

FREQ_MAP = {}
for key,value in [
  ("CLOCKOUT_FREQ_32KHZ", 32768),("CLOCKOUT_FREQ_16KHZ", 16384),
  ("CLOCKOUT_FREQ_8KHZ",   8192),("CLOCKOUT_FREQ_4KHZ",   4096),
  ("CLOCKOUT_FREQ_2KHZ",   2024),("CLOCKOUT_FREQ_1KHZ",   1024),
  ("CLOCKOUT_FREQ_32HZ",     32),("CLOCKOUT_FREQ_1HZ",       1)]:
  if hasattr(Clock,key):
    FREQ_MAP[getattr(Clock,key)] = value

if hasattr(board,'NEOPIXEL'):
  import neopixel_write
  led                 = DigitalInOut(board.NEOPIXEL)
  led.direction       = Direction.OUTPUT
  led_power           = DigitalInOut(board.NEOPIXEL_POWER)
  led_power.direction = Direction.OUTPUT
  led_value           = bytearray([255,0,0])  # GRB
else:
  led           = DigitalInOut(board.LED)
  led.direction = Direction.OUTPUT

if PIN_INT:
  intpin           = DigitalInOut(PIN_INT)
  intpin.direction = Direction.INPUT
  if INT_ACT:
    intpin.pull      = Pull.DOWN
  else:
    intpin.pull      = Pull.UP

i2c = busio.I2C(PIN_SCL,PIN_SDA)
rtc = PCF_RTC(i2c)
timer = Timer(rtc.i2c_device)
clock = Clock(rtc.i2c_device)

# --- blink on-board-led   ---------------------------------------------------

def blink(dur=LED_TIME,repeat=1):
  while repeat:
    if hasattr(board,'NEOPIXEL'):
      led_power.value = 1
      neopixel_write.neopixel_write(led,led_value)
      time.sleep(dur)
      led_power.value = 0
    else:
      led.value = 1
      time.sleep(dur)
      led.value = 0
    if repeat > 1:
      time.sleep(dur)
    repeat -= 1

# --- print current time   ---------------------------------------------------

def print_time(ts):
  """ print current time """
  return "{0:02d}:{1:02d}:{2:02d}".format(ts.tm_hour,ts.tm_min,ts.tm_sec)

# --- enable CLKOUT   --------------------------------------------------------

def enable_clkout(freq):
  """ wrapper for enable CLKOUT """
  clock.clockout_frequency = freq
  if hasattr(clock,"clockout_enabled"):
    clock.clockout_enabled = True

# --- disable CLKOUT   -------------------------------------------------------

def disable_clkout():
  """ wrapper for different methods to disable CLKOUT """
  if hasattr(clock,"clockout_enabled"):
    clock.clockout_enabled = False
  else:
    clock.clockout_frequency = clock.CLOCKOUT_FREQ_DISABLED

# --- get timer-clock and value   --------------------------------------------

def set_timer(delay):
  """set countdown-timer in external RTC to the given delay in seconds"""
  if delay < 0.0000244:
    raise ValueError("delay too small")
  elif delay <= 0.062256:
    timer.timer_frequency = timer.TIMER_FREQ_4KHZ
    timer.timer_value = min(round(delay*4096),255)
  elif delay <= 3.984375:
    timer.timer_frequency = timer.TIMER_FREQ_64HZ
    timer.timer_value = min(round(delay*64),255)
  elif delay <= 255:
    timer.timer_frequency = timer.TIMER_FREQ_1HZ
    timer.timer_value = delay
  elif delay <= 15300:
    timer.timer_frequency = timer.TIMER_FREQ_1_60HZ
    timer.timer_value = min(round(delay/60),255)
  elif hasattr(rtc,"lost_power") and delay <= 918000:
    # only supported on PCF8523
    timer.timer_frequency = timer.TIMER_FREQ_1_3600HZ
    timer.timer_value = min(round(delay/3600),255)
  else:
    raise ValueError("delay too large")

# --- test 0   ---------------------------------------------------------------

def test0():
  """ Test0: alarm """
  print(f"running test0 (alarm flag): alarm in {ALARM_TIME}s")
  for n in range(REPEAT_LOW):
    rtc.alarm_status = False
    dt = rtc.datetime
    print(f"{n}. time before alarm: ", print_time(dt))
    alarm_time = time.localtime(time.mktime(dt) + ALARM_TIME)
    print(f"{n}. time at alarm:     ", print_time(alarm_time))
    rtc.alarm = (alarm_time,"daily")
    while not rtc.alarm_status:
      pass
    # timer fired, print and blink
    print(f"{n}. time after alarm:  ", print_time(rtc.datetime))
    blink()

# --- test 1   ---------------------------------------------------------------

def test1():
  """ Test1: low-frequency timer, checking timer-flag """
  print(f"running test1 (timer flag): delay: {DELAY_TIME_LOW}")
  timer.timer_conf   = 0b1         # note: PCF8563: 1 bit, PCF8523: 2 bits
  timer.timer_status    = False
  set_timer(DELAY_TIME_LOW)
  print(f"{timer.timer_frequency=} ({timer.timer_frequency:#b})")
  for n in range(REPEAT_LOW):
    start = time.monotonic()
    timer.timer_conf = 0b1            # note: PCF8563: 1 bit, PCF8523: 2 bits
    print(f"{timer.timer_conf=} ({timer.timer_conf:#b})")
    while not timer.timer_status:
      print(f"waiting... (rest: {timer.timer_value})")
      time.sleep(1)
    # timer fired, reset and blink
    elapsed = time.monotonic() - start
    timer.timer_conf = 0
    timer.timer_status  = False
    print(f"elapsed: {elapsed}")
    blink()

# --- test 2   ---------------------------------------------------------------

def test2():
  """ Test2: low-frequency timer, checking interrupt-pin """
  print(f"running test2 (interrupt): delay: {DELAY_TIME_LOW}")
  timer.timer_enabled   = 0
  timer.timer_status    = False
  set_timer(DELAY_TIME_LOW)
  timer.timer_interrupt = True
  for n in range(REPEAT_LOW):
    start = time.monotonic()
    timer.timer_enabled   = 1
    while intpin.value != INT_ACT:
      pass
    # timer fired, reset and blink
    elapsed = time.monotonic() - start
    timer.timer_enabled   = 0
    timer.timer_status    = False
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
    timer.timer_enabled   = 1
    while time.monotonic() < end:          # run for (at least) test-period
      while not timer.timer_status:
        pass
      # timer fired: reset and wait for next elapsed timer
      timer.timer_status = False
      counter += 1
    mean_delay = (time.monotonic()-start)/counter
    timer.timer_enabled = 0
    print(f"delay requested: {DELAY_TIME_HIGH}")
    print(f"delay observed:  {mean_delay} (mean of {counter} alarms)")

# --- test 4   ---------------------------------------------------------------

def test4():
  """ Test4: high-frequency timer, counting interrupt-pin """
  print(f"running test4 (interrupt): delay: {DELAY_TIME_HIGH}, duration: {DURATION_TIME_HIGH}")
  set_timer(DELAY_TIME_HIGH)
  timer.timer_interrupt = True
  for n in range(REPEAT_HIGH):             # repeat complete test
    counter = 0
    start = time.monotonic()
    end   = start + DURATION_TIME_HIGH
    timer.timer_enabled   = 1
    while time.monotonic() < end:          # run for (at least) test-period
      while intpin.value != INT_ACT:
        pass
      # timer fired: reset and wait for next elapsed timer
      timer.timer_status = False
      counter += 1
    mean_delay = (time.monotonic()-start)/counter
    timer.timer_enabled = 0
    print(f"delay requested: {DELAY_TIME_HIGH}")
    print(f"delay observed:  {mean_delay} (mean of {counter} alarms)")

# --- test 5   ---------------------------------------------------------------

def test5():
  """ Test5: CLKOUT counter (must be last test)"""
  print(f"running test5 (clockout): freq: {FREQ_MAP[CLKOUT_FREQ]}, duration: {DURATION_TIME_HIGH}")

  # PCF8523 share INT and CLKOUT, so disable interrupt and reset pin
  timer.timer_interrupt = False
  timer.timer_enabled = 0
  intpin.deinit()

  counter = countio.Counter(pin=PIN_COUT,edge=countio.Edge.RISE,
                            pull=Pull.UP)
  for n in range(REPEAT_HIGH):             # repeat complete test
    counter.reset()
    enable_clkout(CLKOUT_FREQ)
    time.sleep(DURATION_TIME_HIGH)
    disable_clkout()
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
disable_clkout()
timer.timer_conf     = 0
timer.timer_interrupt   = False
timer.timer_status      = False
timer.timer_pulsed      = False

print(f"{rtc.lost_power=}")

# execute tests
for tst in [globals()[f"test{i}"] for i in TESTS]:
  tst()
