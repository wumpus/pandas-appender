import pandas as pd


from . import hints


class DF_Appender(object):
    def __init__(self, df=None, chunksize=10000, middles=200, dtypes=None, infer_categories=False, **append_kwargs):
        if isinstance(dtypes, dict):
            self._dtypes = pd.Series(dtypes, dtype='object')
        else:
            self._dtypes = dtypes

        if df is None:
            df = pd.DataFrame()
        elif dtypes is None:  # df, no dtypes
            self._dtypes = df.dtypes
            if infer_categories:
                self._infer_and_merge(df)
                df = df.astype(self._dtypes)
            else:
                self._dtypes = df.dtypes
        else:  # df and dtypes
            if infer_categories:
                self._infer_and_merge(df)
            df = df.astype(self._dtypes)
        self._df = df
        self._chunksize = chunksize
        self._small = []
        self._middle_count = middles
        self._middles = []
        self._infer_categories = infer_categories
        self._append_kwargs = append_kwargs
        for key in append_kwargs:
            if key not in {'ignore_index', 'verify_integrity', 'sort'}:
                raise ValueError('unexpected kwarg '+key)

    def append(self, other, **kwargs):
        if kwargs:
            raise ValueError('unexpected keyword, should you move it to init()? '+repr(kwargs))

        self._small.append(other)
        if len(self._small) > self._chunksize:
            self._merge_small()
        return self  # mimic pd.DataFrame.append return value

    def finalize(self):
        self._merge_small()
        self._merge_middles()
        return self._df

    def _infer_and_merge(self, df):
        inferred = hints.infer_categories(df)
        if self._dtypes is None:
            self._dtypes = pd.Series([], dtype='object')
        self._dtypes = inferred.combine_first(self._dtypes)
        self._infer_categories = False

    def _merge_small(self):
        if not self._small:
            return
        else:
            df = pd.DataFrame()

        df = df.append(self._small, **self._append_kwargs)

        if self._infer_categories:
            self._infer_and_merge(df)

        if self._dtypes is not None:
            df = df.astype(self._dtypes)

        self._middles.append(df)
        self._small = []
        if len(self._middles) > self._middle_count:
            self._merge_middles()

    def _merge_middles(self):
        if not self._middles:
            return
        self._df = pd.concat((self._df, *self._middles), **self._append_kwargs)
        self._middles = []
