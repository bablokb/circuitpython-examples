# copying a large dictionary

import time

ticks_us = lambda: int(time.monotonic_ns() // 1000)
ticks_diff = lambda a, b: a - b

def run():
  a = {i: 2 * i for i in range(1000)}
  b = a.copy()
  for i in range(1000):
    z = i + b[i]
  print(len(b))

t0 = ticks_us()
run()
t1 = ticks_us()
print(f"elapsed: {ticks_diff(t1, t0)}")
