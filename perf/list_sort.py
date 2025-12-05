# test large list sorting (should not stack overflow)

import time

ticks_us = lambda: int(time.monotonic_ns() // 1000)
ticks_diff = lambda a, b: a - b

def run():
  l = list(range(2000))
  l.sort()
  print(l[0], l[-1])
  l.sort(reverse=True)
  print(l[0], l[-1])

t0 = ticks_us()
run()
t1 = ticks_us()
print(f"elapsed: {ticks_diff(t1, t0)}")
