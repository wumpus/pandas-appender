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

        pdfa = PDF_Appender(df, ignore_index=True)  # adding to the previous df
        pdfa.append({'a': a})
        df = pdfa.finalize()
        assert len(df) == a + 1, 'appending dicts to previous df'
        assert np.array_equal(df['a'].values, np.array(range(a+1)))

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


def test_hints():
    dtypes = pd.Series({'a': 'float64', 'b': 'int64'})

    pdfa = PDF_Appender(ignore_index=True, chunksize=2, dtypes=dtypes)
    for aa in range(10):
        pdfa.append({'a': aa, 'b': aa})
    df = pdfa.finalize()
    assert df.dtypes.equals(dtypes)

    dtypes_dict = {'a': 'float64', 'b': 'int64'}
    pdfa = PDF_Appender(ignore_index=True, chunksize=2, dtypes=dtypes_dict)
    for aa in range(10):
        pdfa.append({'a': aa, 'b': aa})
    df = pdfa.finalize()
    assert df.dtypes.equals(dtypes), 'dtype as dict works the same as dtype'

    dtypes = pd.Series({'a': 'category', 'b': 'int64'})

    pdfa = PDF_Appender(ignore_index=True, chunksize=2, dtypes=dtypes)
    with pytest.raises(TypeError):
        for aa in range(10):
            pdfa.append({'a': [aa], 'b': aa})  # a value is unhashable type 
        df = pdfa.finalize()


def test_infer_categories():
    pdfa = PDF_Appender(ignore_index=True, infer_categories=True)
    for aa in range(100):
        # range has to be big enough that the category saves memory: 100 not 10
        pdfa.append({'a': 0, 'b': aa})
    df = pdfa.finalize()
    dtypes = df.dtypes
    assert dtypes['a'] == 'category'

    pdfa = PDF_Appender(df, ignore_index=True)
    with pytest.raises(TypeError):
        pdfa.append({'a': [0], 'b': 3})  # unhashable type
        pdfa.finalize()


@pytest.mark.xfail(reason='chunksize too small for infer categories to fire')
def test_infer_categories_xfail():
    pdfa = PDF_Appender(ignore_index=True, chunksize=2, infer_categories=True)
    for aa in range(100):
        pdfa.append({'a': 0, 'b': aa})
    df = pdfa.finalize()
    dtypes = df.dtypes
    assert dtypes['a'] == 'category'


def test_dtypes_infer_combinations():
    # no df, both dtypes and infer
    dtypes = {'a': 'int32', 'b': 'float32'}
    pdfa = PDF_Appender(ignore_index=True, dtypes=dtypes, infer_categories=True)
    for aa in range(100):
        pdfa.append({'a': 0, 'b': aa})
    df = pdfa.finalize()
    assert df.dtypes['a'] == 'category', 'no df, yes dtypes and infer, infer wins'
    assert df.dtypes['b'] == 'float32', 'no df, yes dtypes and infer, dtype is used'

    df = df.astype({'a': 'int64'})
    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'float32', 'astype did not change b'

    pdfa = PDF_Appender(df, ignore_index=True, infer_categories=True)
    pdfa.append({'a': 0, 'b': 0})
    df2 = pdfa.finalize()
    assert df2.dtypes['a'] == 'category'
    assert df2.dtypes['b'] == 'float32'

    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'float32'
    dtypes = {'b': 'float64'}
    pdfa = PDF_Appender(df, ignore_index=True, dtypes=dtypes)
    pdfa.append({'a': 0, 'b': 0})
    df2 = pdfa.finalize()
    assert df2.dtypes['a'] == 'int64'
    assert df2.dtypes['b'] == 'float64'

    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'float32'
    pdfa = PDF_Appender(df, ignore_index=True, dtypes=dtypes, infer_categories=True)
    pdfa.append({'a': 0, 'b': 0})
    df2 = pdfa.finalize()
    assert df2.dtypes['a'] == 'category'
    assert df2.dtypes['b'] == 'float64'


def test_stress():
    a = 1000000  # around 1 second for 1 million
    pdfa = PDF_Appender(ignore_index=True)
    for aa in range(a):
        pdfa = pdfa.append({'a': aa})  # also testing return value of .append()
    df = pdfa.finalize()
    assert len(df) == a, 'appending one million dicts'
    assert np.array_equal(df['a'].values, np.array(range(a)))


def test_errors():
    with pytest.raises(ValueError):
        pdfa = PDF_Appender(asdf=True)
    pdfa = PDF_Appender()
    with pytest.raises(ValueError):
        pdfa.append({'a': 1}, ignore_index=True)
