from functools import partial
import timeit

from pandas_appender import PDF_Appender


def do_one(total, chunksize, middles):
    pdfa = PDF_Appender(chunksize=chunksize, middles=middles, ignore_index=True)
    for a in range(total):
        pdfa.append({'a': a})
    pd = pdfa.finalize()
    assert len(pd) == total


total = 1_000_000

for chunksize in (1000, 2000, 2500, 5000):
    for middles in (5, 10, 20, 50):
        par = partial(do_one, total, chunksize, middles)
        t = timeit.timeit(par, number=1)
        print('total={} chunksize={} middles={} time={}'.format(total, chunksize, middles, t))
