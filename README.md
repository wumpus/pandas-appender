# pandas-appender

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

pdfa = PDF_appender(ignore_index=True)
for i in range(1_000_000):
    pdfa.append({'i': i})

df = pdfa.finalize()
```

## TODO

Add a `df_template` argument so that columns with `dtype='category'`
can be efficiently represented. Or, make this template from the df
passed in?

