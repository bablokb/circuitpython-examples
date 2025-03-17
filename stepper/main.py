# -------------------------------------------------------------------------
# main.py: Run stepper-motor with ULN2003A-driver.
#
# Author: Bernhard Bablok
# License: MIT
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import time
import board
import uln2003a
import asyncio

PINS = [board.GP10,board.GP11,board.GP12,board.GP13]

async def rotate(*args):
  print("start rotate...")
  t = asyncio.create_task(motor.rotate(*args))
  asyncio.gather(t)
  print("sleeping for 10 seconds")
  await asyncio.sleep(10)
  print("stopping...")
  motor.stop()

# --- main program   ---------------------------------------------------------

# set test-parameters: rotation in degrees and rpm
PARAMETERS = [
  (0.5,4,1),    # two rotations forward at 4 rpm
  (0.5,8,-1)    # four rotations backward at 8 rpm
  ]

motor = uln2003a.FullStepMotor(*PINS,uln2003a.Motor.GEAR_RATIO_16,debug=True)

asyncio.run(rotate(1,4))
time.sleep(2)

for param in PARAMETERS:
  steps = int(param[0] * motor.steps360)
  dir = "forward" if param[2]==1 else "backward"
  print(f"{param[0]} rotations at {param[1]} rpm {dir} ({steps} steps)")
  start = time.monotonic()
  motor.step_degrees(360*param[0]*param[2],rpm=param[1])
  print(f"duration: {time.monotonic()-start:0.1f}")
  time.sleep(2)

motor.step_to_angle(90)


print("test finished")
while True:
  time.sleep(1)
