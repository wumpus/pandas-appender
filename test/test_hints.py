import pandas as pd

import pandas_appender.hints as hints


def test_infer_categories():
    dfl = []
    for aa in range(100):
        dfl.append({'a': 0, 'b': aa})
    df = pd.DataFrame(dfl)
    orig_dtypes = df.dtypes
    inferred = hints.infer_categories(df)
    assert inferred.equals(pd.Series({'a': 'category'}))
    assert df.dtypes.equals(orig_dtypes), 'dtypes was not changed by the infer call'

    df2 = df.astype(inferred)
    assert df.dtypes.equals(orig_dtypes), 'dtypes was not changed by the astype call'

    df_size = df.memory_usage(deep=True).sum()
    df2_size = df2.memory_usage(deep=True).sum()
    assert df2_size < df_size, 'category made it smaller'

    df = df.drop(columns=['a'])
    inferred = hints.infer_categories(df)
    assert inferred.equals(pd.Series([], dtype='object')), 'column b still not a good category'

    dfl = []
    for aa in range(100):
        dfl.append({'a': 0, 'b': [aa]})
    df = pd.DataFrame(dfl)
    inferred = hints.infer_categories(df)
    assert inferred.equals(pd.Series({'a': 'category'}))


def test_determine_dtype():
    tests = [
        [(0, 1), 'int64'],
        [(0, 1.0), 'float64'],
        [(0, float('nan')), 'float64'],
        [(0, None), 'float64'],
        [(0, 'foo'), 'object'],
        [(None, 'foo'), 'object'],
        [(None,), 'object'],
        [(0,), 'int64'],
    ]
    for t in tests:
        data, dtype = t
        assert hints.determine_dtype(data) == dtype


def test_harmonize():
    array_i = []
    array_ici = []
    array_icf = []
    array_f = []
    array_fci = []
    array_fcf = []
    for i in range(100):
        f = float(i)
        array_i.append({'a': i, 'aa': i})
        array_ici.append({'a': 0, 'aa': i})
        array_icf.append({'a': 0.0, 'aa': i})
        array_f.append({'a': i, 'aa': f})
        array_fci.append({'a': 0, 'aa': f})
        array_fcf.append({'a': 0.0, 'aa': f})
    df_i = pd.DataFrame(array_i)
    df_ici = pd.DataFrame(array_ici)
    df_icf = pd.DataFrame(array_icf)
    df_f = pd.DataFrame(array_f)
    df_fci = pd.DataFrame(array_fci)
    df_fcf = pd.DataFrame(array_fcf)

    # manufacture df with actual categoreis
    df_ici['a'] = pd.Series(df_ici['a'], dtype='category')
    df_icf['a'] = pd.Series(df_icf['a'], dtype='category')
    df_fci['a'] = pd.Series(df_fci['a'], dtype='category')
    df_fcf['a'] = pd.Series(df_fcf['a'], dtype='category')

    # identities are all None
    assert hints.harmonize_types([df_i, df_i]) is None
    assert hints.harmonize_types([df_ici, df_ici]) is None
    assert hints.harmonize_types([df_icf, df_icf]) is None
    assert hints.harmonize_types([df_f, df_f]) is None
    assert hints.harmonize_types([df_fci, df_fci]) is None
    assert hints.harmonize_types([df_fcf, df_fcf]) is None

    # easy cases
    assert hints.harmonize_types([df_i, df_f]) == {'a': 'int64', 'aa': 'float64'}
    assert hints.harmonize_types([df_f, df_i]) == {'a': 'int64', 'aa': 'float64'}
    assert hints.harmonize_types([df_i, df_f, df_f]) == {'a': 'int64', 'aa': 'float64'}
    assert hints.harmonize_types([df_f, df_i, df_i]) == {'a': 'int64', 'aa': 'float64'}

    # non-cat with cat -- no more cat, but it's not none
    assert hints.harmonize_types([df_i, df_ici]) == {'a': 'int64', 'aa': 'int64'}
    assert hints.harmonize_types([df_i, df_icf]) == {'a': 'float64', 'aa': 'int64'}
    assert hints.harmonize_types([df_f, df_fci]) == {'a': 'int64', 'aa': 'float64'}
    assert hints.harmonize_types([df_f, df_fcf]) == {'a': 'float64', 'aa': 'float64'}

    # cross with cats -- no more cats
    assert hints.harmonize_types([df_f, df_ici]) == {'a': 'int64', 'aa': 'float64'}
    assert hints.harmonize_types([df_f, df_icf]) == {'a': 'float64', 'aa': 'float64'}

    # cats with cats preserves the cat
    # (this test can't see the underlying category type)
    assert hints.harmonize_types([df_fci, df_ici]) == {'a': 'category', 'aa': 'float64'}
    assert hints.harmonize_types([df_fcf, df_ici]) == {'a': 'category', 'aa': 'float64'}
    assert hints.harmonize_types([df_fci, df_icf]) == {'a': 'category', 'aa': 'float64'}
    assert hints.harmonize_types([df_fcf, df_icf]) == {'a': 'category', 'aa': 'float64'}
