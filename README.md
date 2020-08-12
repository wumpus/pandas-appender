# pandas-appender

[![Build Status](https://travis-ci.org/wumpus/pandas-appender.svg?branch=master)](https://travis-ci.org/wumpus/pandas-appender) [![Coverage Status](https://coveralls.io/repos/github/wumpus/pandas-appender/badge.svg?branch=master)](https://coveralls.io/github/wumpus/pandas-appender?branch=master) [![Apache License 2.0](https://img.shields.io/github/license/wumpus/pandas-appender.svg)](LICENSE)

Have you ever wanted to append a bunch of rows to a Pandas DataFrame? Turns out that
it's extremely inefficient to do so for a large dataframe, you're supposed to make
multiple dataframes and pd.concat them instead.

So... helper function? Pandas doesn't seem to have one. Roll your own?
OK then. Here's that helper function. It can append around 1 million small
rows per cpu-second, and has modest additional memory usage.

## Install

`pip install pandas-appender`

## Usage

```
from pandas_appender import PDF_Appender

pdfa = PDF_appender(ignore_index=True)  # note that ignore_index moves to the init
for i in range(1_000_000):
    pdfa = pdfa.append({'i': i})

df = pdfa.finalize()
```

## Type hints and category detection

Using narrower types and categories can often dramatically reduce the size of a
DataFrame. There are two ways to do this in pandas-appender. One is to
append to an existing dataframe:

```
pdfa = PDF_appender(df, ignore_index=True)
```

and the second is to pass in a `dtypes=` argument:

```
pdfa = PDF_appender(ignore_index=True, dtypes=another_dataframe.dtypes)
```

pandas-appender also offers a way to infer which columns would be smaller
if they were categories. This code will either analyze an existing dataframe
that you're appending to:
```
pdfa = PDF_appender(df, ignore_index=True, infer_categories=True)
```
or it will analyze the first chunk of appended lines:
```
pdfa = PDF_appender(ignore_index=True, infer_categories=True)
```
These inferred categories will override existing types or a `dtypes=` argument.
