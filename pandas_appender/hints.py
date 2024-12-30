from collections import defaultdict

import pandas as pd


def infer_categories(df, verbose=0):
    '''Helper function that figures out which columns in a dataframe would
    be smaller as a Categorical datatype.

    The return value is a Pandas dtypes containing entries for only the
    columns which are smaller as categories.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    dtypes
    '''
    inferred = {}
    for col in df:
        if df[col].dtype.name == 'category':
            continue
        try:
            category_series = pd.Series(df[col], dtype='category')
        except TypeError:
            # e.g. unhashable type
            continue

        size = df[col].memory_usage(index=False, deep=True)
        csize = category_series.memory_usage(index=False, deep=True)
        if csize < size:
            inferred[col] = 'category'

    if verbose:
        print('infer_categories: picking ', ', '.join(inferred.key()))

    return pd.Series(inferred, dtype='object')  # this is a dtypes


def infer_to_dtypes(cats, dtypes, verbose=0):
    '''Helper function that infers categorical and returns the entire
    dtypes for a dataframe'''
    return cats.combine_first(dtypes)


def determine_dtype(data, verbose=0):
    if verbose:
        print('harmonizing this combination', data)
    df = pd.DataFrame({'col': data})
    dtype = df['col'].dtype
    if verbose:
        print('dtype ends up', dtype.name)
    return dtype.name


def harmonize_types(dfs, verbose=0):
    exemplars = defaultdict(lambda: defaultdict(dict))
    for df in dfs:
        for col in df.columns:
            series = df[col]
            if series.empty:
                continue
            dtype_name = series.dtype.name
            exemplar = series.iat[0]
            exemplars[col][dtype_name] = exemplar

    # for all columns with multiple dtypes, use the DataFrame constructor to pick
    ret = {}
    changes = False
    for col in exemplars:
        if len(exemplars[col]) > 1:
            data = exemplars[col].values()
            dtype = determine_dtype(data, verbose=verbose)
            ret[col] = dtype
            changes = True
        else:
            ret[col] = list(exemplars[col].keys())[0]
    if changes:
        return ret
