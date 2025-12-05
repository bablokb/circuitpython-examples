def bm_run(N, M):
    try:
        from time import ticks_us, ticks_diff
    except ImportError:
        # CIRCUITPY-CHANGE
        import time

        ticks_us = lambda: int(time.monotonic_ns() // 1000)
        ticks_diff = lambda a, b: a - b

    # Pick sensible parameters given N, M
    cur_nm = (0, 0)
    param = None
    for nm, p in bm_params.items():
        if 10 * nm[0] <= 12 * N and nm[1] <= M and nm > cur_nm:
            cur_nm = nm
            param = p
    if param is None:
        print(-1, -1, "SKIP: no matching params")
        return

    # Run and time benchmark
    run, result = bm_setup(param)
    t0 = ticks_us()
    run()
    t1 = ticks_us()
    norm, out = result()
    print(ticks_diff(t1, t0), norm, out)
# Source: https://github.com/python/pyperformance
# License: MIT

# Calculating some of the digits of π.
# This benchmark stresses big integer arithmetic.
# Adapted from code on: http://benchmarksgame.alioth.debian.org/


def compose(a, b):
    aq, ar, as_, at = a
    bq, br, bs, bt = b
    return (aq * bq, aq * br + ar * bt, as_ * bq + at * bs, as_ * br + at * bt)


def extract(z, j):
    q, r, s, t = z
    return (q * j + r) // (s * j + t)


def gen_pi_digits(n):
    z = (1, 0, 0, 1)
    k = 1
    digs = []
    for _ in range(n):
        y = extract(z, 3)
        while y != extract(z, 4):
            z = compose(z, (k, 4 * k + 2, 0, 2 * k + 1))
            k += 1
            y = extract(z, 3)
        z = compose((10, -10 * y, 0, 1), z)
        digs.append(y)
    return digs


###########################################################################
# Benchmark interface

bm_params = {
    (32, 10): (1, 20),
    (50, 25): (1, 35),
    (100, 100): (1, 65),
    (1000, 1000): (2, 250),
    (5000, 1000): (3, 350),
}


def bm_setup(params):
    state = None

    def run():
        nonlocal state
        nloop, ndig = params
        ndig = params[1]
        for _ in range(nloop):
            state = None  # free previous result
            state = gen_pi_digits(ndig)

    def result():
        return params[0] * params[1], "".join(str(d) for d in state)

    return run, result

# execute test
bm_run(133,100)   # MHz, heap in kB
