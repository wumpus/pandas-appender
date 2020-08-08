import pandas as pd


class PDF_Appender(object):
    def __init__(self, df=None, chunksize=2500, middles=10, **append_kwargs):
        if df is None:
            df = pd.DataFrame()
        self._df = df
        self._chunksize = chunksize
        self._small = []
        self._middle_count = middles
        self._middles = []
        self._append_kwargs = append_kwargs
        for key in append_kwargs:
            if key not in {'ignore_index', 'verify_integrity', 'sort'}:
                raise ValueError('unexpected kwarg '+key)

    def append(self, other):
        self._small.append(other)
        if len(self._small) > self._chunksize:
            self._merge_small()

    def finalize(self):
        self._merge_small()
        self._merge_middles()
        return self._df

    def _merge_small(self):
        if not self._small:
            return
        df = pd.DataFrame()
        df = df.append(self._small, **self._append_kwargs)
        self._middles.append(df)
        self._small = []
        if len(self._middles) > self._middle_count:
            self._merge_middles()

    def _merge_middles(self):
        if not self._middles:
            return
        self._df = pd.concat((self._df, *self._middles), **self._append_kwargs)
        self._middles = []
