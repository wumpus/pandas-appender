
import pandas as pd
import numpy as np
import pytest

from pandas_appender import DF_Appender


def test_basics():
    for a in range(1, 5):
        dfa = DF_Appender(ignore_index=True)
        for aa in range(a):
            dfa.append({'a': aa})
        df = dfa.finalize()
        assert len(df) == a, 'appending dicts'
        assert np.array_equal(df['a'].values, np.array(range(a)))

        dfa = DF_Appender(df, ignore_index=True)  # adding to the previous df
        dfa.append({'a': a})
        df = dfa.finalize()
        assert len(df) == a + 1, 'appending dicts to previous df'
        assert np.array_equal(df['a'].values, np.array(range(a+1)))

    for a in range(1, 5):
        dfa = DF_Appender()
        for aa in range(a):
            dfa.append({'a': aa})
        df = dfa.finalize()
        assert len(df) == a, 'appending dicts, ignore_index=False'
        assert np.array_equal(df['a'].values, np.array(range(a)))

    for a in range(1, 5):
        dfa = DF_Appender(chunksize=1, ignore_index=True)
        for aa in range(a):
            dfa.append({'a': aa})
        df = dfa.finalize()
        print(df)
        assert len(df) == a, 'appending dicts, minimum chunksize'
        assert np.array_equal(df['a'].values, np.array(range(a)))

    for a in range(1, 5):
        dfa = DF_Appender(ignore_index=True)
        for aa in range(a):
            dfa.append(pd.Series([aa], name='a'))
        df = dfa.finalize()
        print(df)
        assert len(df) == a, 'appending pd.Series of length 1'
        #assert np.array_equal(df['a'].values, np.array(range(a)))  # gets column name of '0'

    # you can't pass a list of df to the df constructor
    #for a in range(1, 5):
    #    dfa = DF_Appender(ignore_index=True)
    #    for aa in range(a):
    #        dfa.append(pd.DataFrame([{'a': aa}]))
    #    df = dfa.finalize()
    #    assert len(df) == a, 'appending pd.Dataframe of length 1'
    #    assert np.array_equal(df['a'].values, np.array(range(a)))


def test_hints():
    dtypes = pd.Series({'a': 'float64', 'b': 'int64'})

    dfa = DF_Appender(ignore_index=True, chunksize=2, dtypes=dtypes)
    for aa in range(10):
        dfa.append({'a': aa, 'b': aa})
    df = dfa.finalize()
    assert df.dtypes.equals(dtypes)

    dtypes_dict = {'a': 'float64', 'b': 'int64'}
    dfa = DF_Appender(ignore_index=True, chunksize=2, dtypes=dtypes_dict)
    for aa in range(10):
        dfa.append({'a': aa, 'b': aa})
    df = dfa.finalize()
    assert df.dtypes.equals(dtypes), 'dtype as dict works the same as dtype'


def test_infer_categories():
    dfa = DF_Appender(ignore_index=True, infer_categories=True)
    for aa in range(100):
        # range has to be big enough that the category saves memory: 100 not 10
        dfa.append({'a': 0, 'b': aa})
    df = dfa.finalize()
    dtypes = df.dtypes
    assert dtypes['a'] == 'category'


@pytest.mark.xfail(reason='chunksize too small for infer categories to fire')
def test_infer_categories_xfail():
    dfa = DF_Appender(ignore_index=True, chunksize=2, infer_categories=True)
    for aa in range(100):
        dfa.append({'a': 0, 'b': aa})
    df = dfa.finalize()
    dtypes = df.dtypes
    assert dtypes['a'] == 'category'


def test_dtypes_infer_combinations():
    # no df, both dtypes and infer
    dtypes = {'a': 'int32', 'b': 'float32'}
    dfa = DF_Appender(ignore_index=True, dtypes=dtypes, infer_categories=True)
    for aa in range(100):
        dfa.append({'a': 0, 'b': aa})
    df = dfa.finalize()
    assert df.dtypes['a'] == 'category', 'no df, yes dtypes and infer, infer wins'
    assert df.dtypes['b'] == 'float32', 'no df, yes dtypes and infer, dtype is used'

    df = df.astype({'a': 'int64'})
    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'float32', 'astype did not change b'

    # df, infer, no dtype
    dfa = DF_Appender(df, ignore_index=True, infer_categories=True)
    dfa.append({'a': 0, 'b': 0})
    df2 = dfa.finalize()
    assert df2.dtypes['a'] == 'category'
    assert df2.dtypes['b'] == 'float64'  # type altered because it was merged with int64

    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'float32', 'passing in df did not alter df'

    # df, no infer, dtypes
    dtypes = {'b': 'float64'}
    dfa = DF_Appender(df, ignore_index=True, dtypes=dtypes)
    dfa.append({'a': 0, 'b': 0})
    df2 = dfa.finalize()
    assert df2.dtypes['a'] == 'int64'
    assert df2.dtypes['b'] == 'float64'

    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'float32'

    # df, types, infer
    dfa = DF_Appender(df, ignore_index=True, dtypes=dtypes, infer_categories=True)
    dfa.append({'a': 0, 'b': 0})
    df2 = dfa.finalize()
    assert df2.dtypes['a'] == 'category'
    assert df2.dtypes['b'] == 'float64'


def test_stress():
    a = 1000000  # around 1 second for 1 million
    dfa = DF_Appender(ignore_index=True)
    for aa in range(a):
        dfa = dfa.append({'a': aa})  # also testing return value of .append()
    df = dfa.finalize()
    assert len(df) == a, 'appending one million dicts'
    assert np.array_equal(df['a'].values, np.array(range(a)))


def test_errors():
    with pytest.raises(ValueError):
        dfa = DF_Appender(asdf=True)
    dfa = DF_Appender()
    with pytest.raises(ValueError):
        dfa.append({'a': 1}, ignore_index=True)

    dfa = DF_Appender()
    df = dfa.finalize()
    assert len(df) == 0


@pytest.mark.xfail(reason='pandas-append behaves differently from DataFrame.append')
def test_inconsistant_types():
    # pass in df, append something bad
    df = pd.DataFrame([{'a': 128}])
    df = df.astype({'a': 'int64'})
    assert df['a'].dtype == 'int64', 'this one actually passes'

    dfa = DF_Appender(df, ignore_index=True)
    dfa = dfa.append({'a': 0.1})
    df2 = dfa.finalize()
    # DF_Appender converts 0.1 to the integer 0

    df3 = df.append({'a': 0.1}, ignore_index=True)
    # at this point Pandas has promoted the type of a to 'float64'

    assert df2['a'].dtype == df3['a'].dtype
    assert df2.equals(df3), 'dfa same odd result as df.append'

    dfa = DF_Appender(ignore_index=True, dtypes={'a': 'int64'})
    dfa = dfa.append({'a': 0.1})
    df2 = dfa.finalize()
    # DF_Appender converts 0.1 to the integer 0

    assert df2['a'].dtype == df3['a'].dtype
    assert df2.equals(df3), 'dfa same odd result as df.append, another way'
