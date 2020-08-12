import pandas as pd


def infer_categories(df):
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
