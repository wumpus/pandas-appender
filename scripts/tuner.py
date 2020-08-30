from functools import partial
import timeit
from collections import defaultdict
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pandas_appender import DF_Appender


def do_one(total, chunksize):
    #dtypes = None
    #dtypes = {'a': 'int64', 'b': 'int64', 'c': 'int64', 'd': 'int64', 'e': 'int64', 'f': 'int64'}
    dtypes = {'a': 'float64', 'b': 'float64', 'c': 'float64', 'd': 'float64', 'e': 'float64', 'f': 'float64'}
    dfa = DF_Appender(chunksize=chunksize, dtypes=dtypes, ignore_index=True)
    for a in range(total):
        #dfa.append({'a': a})
        dfa.append({'a': a, 'b': a, 'c': a, 'd': a, 'e': a, 'f': a})
    t0 = time.time()
    df = dfa.finalize()
    print('total {} chunksize {} finalize_elapsed {:.1f}'.format(total, chunksize, time.time() - t0))
    assert len(df) == total


fig = plt.figure(figsize=(6, 6))  # inches
ax = fig.add_subplot(1, 1, 1)

results = defaultdict(list)
xdata = []

totals = (1e5, 5e5, 1e6, 5e6, 1e7, 5e7, 1e8)
chunksizes = (2000, 5000, 10000, 20000)

for total in totals:
    total = int(total)
    xdata.append(total)
    for chunksize in reversed(chunksizes):
        name = 'chunk={}'.format(chunksize)
        par = partial(do_one, total, chunksize)
        t = timeit.timeit(par, number=1)
        perf = total/t / 1000000.
        results[name].append(perf)

xdata = np.array(xdata)
ax.set_xticks(xdata)
ax.ticklabel_format(axis='x', style='sci')
ax.set_xlabel('rows appended')
ax.ticklabel_format(axis='y', style='sci')

for n in results:
    results[n] = np.array(results[n])
    ax.plot(xdata, results[n], 'o-', label=n)

ax.set_title('mega-appends per cpu-second vs. size')
ax.legend(loc='lower left', fontsize='xx-small')

plt.savefig('out.png', dpi=300)
plt.close()
