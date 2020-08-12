from functools import partial
import timeit

from pandas_appender import DF_Appender


def do_one(total, chunksize, middles):
    #dtypes = None
    #dtypes = {'a': 'int64', 'b': 'int64', 'c': 'int64', 'd': 'int64', 'e': 'int64', 'f': 'int64'}
    dtypes = {'a': 'float64', 'b': 'float64', 'c': 'float64', 'd': 'float64', 'e': 'float64', 'f': 'float64'}
    dfa = DF_Appender(chunksize=chunksize, middles=middles, dtypes=dtypes, ignore_index=True, EARLY=True)
    for a in range(total):
        #dfa.append({'a': a})
        dfa.append({'a': a, 'b': a, 'c': a, 'd': a, 'e': a, 'f': a})
    df = dfa.finalize()
    print(df.dtypes)
    print(len(df))
    assert len(df) == total


total = 1_000_000

#for chunksize in (10000, 20000):
#    for middles in (50, 100, 200, 500, 1000, 2000):
for chunksize in (1000, 2000, 2500, 5000, 10000, 20000):
    for middles in (5, 10, 50, 100, 200, 500, 1000, 2000):
        par = partial(do_one, total, chunksize, middles)
        t = timeit.timeit(par, number=1)
        print('total={} chunksize={} middles={} time={}'.format(total, chunksize, middles, t))
