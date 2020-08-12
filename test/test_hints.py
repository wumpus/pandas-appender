import pytest

import pandas as pd

import pandas_appender.hints


def test_infer_categories():
    df = pd.DataFrame()
    for aa in range(100):
        df = df.append({'a': 0, 'b': aa}, ignore_index=True)
    orig_dtypes = df.dtypes
    inferred = pandas_appender.hints.infer_categories(df)
    assert inferred.equals(pd.Series({'a': 'category'}))
    assert df.dtypes.equals(orig_dtypes), 'dtypes was not changed by the infer call'

    df2 = df.astype(inferred)
    assert df.dtypes.equals(orig_dtypes), 'dtypes was not changed by the astype call'

    df_size = df.memory_usage(deep=True).sum()
    df2_size = df2.memory_usage(deep=True).sum()
    assert df2_size < df_size, 'category made it smaller'

    df = df.drop(columns=['a'])
    inferred = pandas_appender.hints.infer_categories(df)
    assert inferred.equals(pd.Series([], dtype='object')), 'column b still not a good category'

    df = pd.DataFrame()
    for aa in range(100):
        df = df.append({'a': 0, 'b': [aa]}, ignore_index=True)
    inferred = pandas_appender.hints.infer_categories(df)
    assert inferred.equals(pd.Series({'a': 'category'}))
