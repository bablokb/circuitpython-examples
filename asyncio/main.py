# -------------------------------------------------------------------------
# Asyncio-example: two coroutine-tasks, repeated execution
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import asyncio
import time

class App:
  async def _cr(self,id,interval,count):
    for _ in range(count):
      print("%f: running %s" % (time.monotonic(),id))
      await asyncio.sleep(interval)

  async def _main(self):
    print("%f: start main" % time.monotonic())
    task1 = asyncio.create_task(self._cr("task1",3,4))
    task2 = asyncio.create_task(self._cr("task2",2,6))

    await asyncio.gather(task1,task2)
    print("%f: done main" % time.monotonic())

  def main(self):
    asyncio.run(self._main())


app = App()
app.main()
time.sleep(3)
app.main()
