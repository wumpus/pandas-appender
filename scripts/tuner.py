from functools import partial
import timeit
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pandas_appender import DF_Appender


def do_one(total, chunksize, middles):
    #dtypes = None
    #dtypes = {'a': 'int64', 'b': 'int64', 'c': 'int64', 'd': 'int64', 'e': 'int64', 'f': 'int64'}
    dtypes = {'a': 'float64', 'b': 'float64', 'c': 'float64', 'd': 'float64', 'e': 'float64', 'f': 'float64'}
    dfa = DF_Appender(chunksize=chunksize, middles=middles, dtypes=dtypes, ignore_index=True)
    for a in range(total):
        #dfa.append({'a': a})
        dfa.append({'a': a, 'b': a, 'c': a, 'd': a, 'e': a, 'f': a})
    df = dfa.finalize()
    assert len(df) == total


fig = plt.figure(figsize=(6, 6))  # inches
#ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])  # left, bottom, width, height
ax = fig.add_subplot(1, 1, 1)

results = defaultdict(list)
xdata = []

#totals = (1e5, 5e5, 1e6, 5e6, 1e7)
#chunksizes = (1000, 2000, 2500, 5000, 10000, 20000)
#middles = (5, 10, 50, 100, 200, 500, 1000, 2000)
#totals = (1e5, 5e5, 1e6, 2e6)
totals = (1e5, 5e5, 1e6, 5e6, 1e7)
chunksizes = (2000, 5000, 10000, 20000)
middles = (10, 20, 50, 100, 200)

for total in totals:
    total = int(total)
    xdata.append(total)
    for chunksize in reversed(chunksizes):
        for middle in reversed(middles):
            name = 'chunk={} m={}'.format(chunksize, middle)
            par = partial(do_one, total, chunksize, middle)
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
