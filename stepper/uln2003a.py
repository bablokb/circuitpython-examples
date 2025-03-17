# -------------------------------------------------------------------------
# uln2003a.py: Driver for ULN2003A.
#
# This code is a modified version of:
#
# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at
# https://RandomNerdTutorials.com/raspberry-pi-pico-stepper-motor-micropython/
# Forked from:
# https://github.com/larsks/micropython-stepper-motor/blob/master/motor.py
#
# Author: Bernhard Bablok
# License: MIT
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import time
import digitalio
import asyncio

class Motor:
  GEAR_RATIO_16 = int(32*16.128)
  GEAR_RATIO_64 = 4*GEAR_RATIO_16
  
  """ base class """
  def __init__(self, p1, p2, p3, p4, states=None, steps360=0, rpm=1, debug=False):
    self._pins     = self._get_dios([p1, p2, p3, p4])
    self._states   = states
    self._steps360 = steps360
    self._spm      = rpm*steps360      # steps per minute for given rpm
    self._tpstep   = 60/self._spm      # time per step in seconds

    self._state = 0
    self._pos = 0
    self._stop = False

    print(f"{self._states}")
    if not debug:
      self._debug = lambda x: None

  def _debug(self,msg):
    """ print debug message """
    print(msg)

  def _get_dios(self, pins):
    dios = []
    for pin in pins:
      dio = digitalio.DigitalInOut(pin)
      dio.direction = digitalio.Direction.OUTPUT
      dios.append(dio)
    return dios

  def _step(self, dir):
    state = self._states[self._state]
    #self._debug(f"_step: {dir=},{self._state=},{state=}")
    for i, val in enumerate(state):
      self._pins[i].value = val
    self._state = (self._state + dir) % len(self._states)
    self._pos = (self._pos + dir) % self._steps360

  def _get_tpstep(self,rpm):
    """ query time per step for given rpm """
    if rpm is None:
      return self._tpstep
    else:
      return 60/(rpm*self._steps360)
    
  @property
  def pos(self):
    return self._pos

  @pos.setter
  def pos(self,value):
    self._pos = value

  def stop(self):
    self._stop = True

  @property
  def steps360(self):
    return self._steps360

  def step(self, steps,rpm=None):
    dir = 1 if steps >= 0 else -1
    steps = abs(steps)
    tpstep = self._get_tpstep(rpm)
    self._debug(f"step: {self.pos=}, {steps=}, {tpstep=}")
    for _ in range(0,steps):
      t_start = time.monotonic()
      self._step(dir)
      time.sleep(tpstep - (time.monotonic()-t_start))

  async def rotate(self, dir, rpm=None):
    self._stop = False
    tpstep = self._get_tpstep(rpm)
    self._debug(f"rotate: {self.pos=}, {tpstep=}")
    while not self._stop:
      t_start = time.monotonic()
      self._step(dir)
      await asyncio.sleep(tpstep - (time.monotonic()-t_start))

  def step_to_target(self, target, dir=None, rpm=None):
    """ step to target position """
    target = int(target%self._steps360)
    if dir is None:
      dir = 1 if target > self._pos else -1
      if abs(target - self._pos) > self._steps360/2:
        dir = -dir

    steps = target - self._pos
    if dir == 1:
      if steps < 0:
        steps += self._steps360
    else:
      if steps > 0:
        steps = -steps

    self._debug(f"step_to_target: {self.pos=}, {steps=}")
    self.step(steps,rpm)

  def step_to_angle(self, angle, dir=None, rpm=None):
    """ step to target angle. Use shortest path unless dir is given """
    target = int((angle%360)/360*self._steps360)
    self._debug(f"step_to_angle: {self.pos=}, {target=}")
    self.step_to_target(target, dir=dir, rpm=rpm)
    self._debug(f"step_to_angle: {self.pos=}")

  def step_degrees(self, degrees, rpm=None):
    steps = int(degrees / 360 * self._steps360)
    self._debug(f"step_degrees: {self.pos=}, {steps=}")
    self.step(steps, rpm=rpm)
    self._debug(f"step_degrees: {self.pos=}")

class FullStepMotor(Motor):
  def __init__(self, p1, p2, p3, p4,ratio,rpm=1,debug=False):
    states = [
      [1, 1, 0, 0],
      [0, 1, 1, 0],
      [0, 0, 1, 1],
      [1, 0, 0, 1]
    ]
    super().__init__(p1,p2,p3,p4,states,ratio,rpm,debug)

class HalfStepMotor(Motor):
  def __init__(self, p1, p2, p3, p4,ratio,rpm=1,debug=False):
    states = [
      [1, 0, 0, 0],
      [1, 1, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 1, 0],
      [0, 0, 1, 0],
      [0, 0, 1, 1],
      [0, 0, 0, 1],
      [1, 0, 0, 1],
    ]
    super().__init__(p1,p2,p3,p4,states,ratio,rpm,debug)
