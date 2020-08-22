import pandas as pd


def infer_categories(df):
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
        try:
            category_series = pd.Series(df[col], dtype='category')
        except TypeError:
            # e.g. unhashable type
            continue

        size = df[col].memory_usage(index=False, deep=True)
        csize = category_series.memory_usage(index=False, deep=True)
        if csize < size:
            inferred[col] = 'category'

    return pd.Series(inferred, dtype='object')
