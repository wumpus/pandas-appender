import pandas as pd
import numpy as np
import pytest

from pandas_appender import PDF_Appender

# can append: df, series, dict-like, or list of these
#   if you append a list of dicts, you end up with a column of objects
# always test ignore_index=True


def test_basics():
    for a in range(1, 5):
        pdfa = PDF_Appender(ignore_index=True)
        for aa in range(a):
            pdfa.append({'a': aa})
        df = pdfa.finalize()
        assert len(df) == a, 'appending dicts'
        assert np.array_equal(df['a'].values, np.array(range(a)))

    for a in range(1, 5):
        pdfa = PDF_Appender()
        for aa in range(a):
            pdfa.append({'a': aa})
        df = pdfa.finalize()
        assert len(df) == a, 'appending dicts, ignore_index=False'
        assert np.array_equal(df['a'].values, np.array(range(a)))

    for a in range(1, 5):
        pdfa = PDF_Appender(chunksize=1, middles=1, ignore_index=True)
        for aa in range(a):
            pdfa.append({'a': aa})
        df = pdfa.finalize()
        print(df)
        assert len(df) == a, 'appending dicts, minimum counts'
        assert np.array_equal(df['a'].values, np.array(range(a)))

    for a in range(1, 5):
        pdfa = PDF_Appender(ignore_index=True)
        for aa in range(a):
            pdfa.append(pd.Series([aa], name='a'))
        df = pdfa.finalize()
        print(df)
        assert len(df) == a, 'appending pd.Series of length 1'
        #assert np.array_equal(df['a'].values, np.array(range(a)))  # gets column name of '0'

    for a in range(1, 5):
        pdfa = PDF_Appender(ignore_index=True)
        for aa in range(a):
            pdfa.append(pd.DataFrame([{'a': aa}]))
        df = pdfa.finalize()
        assert len(df) == a, 'appending pd.Dataframe of length 1'
        assert np.array_equal(df['a'].values, np.array(range(a)))


def test_preexist():
    starting_df = pd.DataFrame([{'a': a} for a in range(10)])
    pdfa = PDF_Appender(starting_df, ignore_index=True)
    for aa in range(10, 20):
        pdfa.append({'a': aa})
    df = pdfa.finalize()
    assert len(df) == 20
    assert np.array_equal(df['a'].values, np.array(range(20)))


def test_stress():
    a = 1000000  # around 1 second for 1 million
    pdfa = PDF_Appender(ignore_index=True)
    for aa in range(a):
        pdfa.append({'a': aa})
    df = pdfa.finalize()
    assert len(df) == a, 'appending one million dicts'
    assert np.array_equal(df['a'].values, np.array(range(a)))


def test_errors():
    with pytest.raises(ValueError):
        pdfa = PDF_Appender(asdf=True)
