# pandas-appender

[![Build Status](https://dev.azure.com/lindahl0577/pandas-appender/_apis/build/status/wumpus.pandas-appender?branchName=master)](https://dev.azure.com/lindahl0577/pandas-appender/_build/latest?definitionId=2&branchName=master) [![Coverage](https://coveralls.io/repos/github/wumpus/pandas-appender/badge.svg?branch=master)](https://coveralls.io/github/wumpus/pandas-appender?branch=master) [![Apache License 2.0](https://img.shields.io/github/license/wumpus/pandas-appender.svg)](LICENSE)

Have you ever wanted to append a bunch of rows to a Pandas DataFrame? Turns out that
it's extremely inefficient to do so for a large dataframe, you're supposed to make
multiple dataframes and pd.concat them instead.

So... helper function? Pandas doesn't seem to have one. Roll your own?
OK then. Here's that helper function. It can append around 1 million
very small rows per cpu-second, and has a modest additional memory
usage of around 5 megabytes, dynamically growing with the number of
rows appended.

## Install

`pip install pandas-appender`

## Usage

```
from pandas_appender import DF_Appender

dfa = DF_appender(ignore_index=True)  # note that ignore_index moves to the init
for i in range(1_000_000):
    dfa = dfa.append({'i': i})

df = dfa.finalize()
```

## Type hints and category detection

Using narrower types and categories can often dramatically reduce the size of a
DataFrame. There are two ways to do this in pandas-appender. One is to
append to an existing dataframe:

```
dfa = DF_appender(df, ignore_index=True)
```

and the second is to pass in a `dtypes=` argument:

```
dfa = DF_appender(ignore_index=True, dtypes=another_dataframe.dtypes)
```

pandas-appender also offers a way to infer which columns would be smaller
if they were categories. This code will either analyze an existing dataframe
that you're appending to:
```
dfa = DF_appender(df, ignore_index=True, infer_categories=True)
```
or it will analyze the first chunk of appended lines:
```
dfa = DF_appender(ignore_index=True, infer_categories=True)
```
These inferred categories will override existing types or a `dtypes=` argument.

## Incompatibilities with pandas.DataFrame.append()

### pandas.DataFame.append is idempotent, DF_Appender is not

* Pandas: `df_new = df.append()  # df is not changed`
* DF_Appender: `dfa_new = dfa.append()  # modifies dfa, and dfa_new == dfa`

### pandas.DataFrame.append will promote types, while DF_Appender is strict 

* Pandas: append `0.1` to an integer column, and the column will be promoted to float
* DF_Appender: when initialized with `dtypes=` or an existing DataFrame, appending
`0.1` to an integer column causes `0.1` to be cast to an integer, i.e. `0`.
