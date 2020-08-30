import pandas as pd


from . import hints


class DF_Appender(object):
    '''A class used to make appending to a Pandas DataFrame efficient.'''

    def __init__(self, df=None, chunksize=5000, dtypes=None, infer_categories=False, **append_kwargs):
        '''Initialize a DF_Appender object.

        Parameters
        ----------
        df : DataFrame or Series/dict-like object, or list of these
            Initialize the DF_Appender with these rows.
        chunksize : int, default 5000
            `chunksize` controls how much extra memory the append algorithm
            uses in order to save cpu time.
        dtypes : str, type, dict, default None
            Initialize the DataFrame with these column dtypes.
        infer_categories : bool, default False
            if True, examine the first chunk of appended rows to determine
            which columns are smaler as dtype 'category'.
        ignore_index : bool, default False
            If True, the resulting axis will be labeled 0, 1, …, n - 1.
        verify_integrity : bool, default False
            If True, raise ValueError on creating index with duplicates.
        sort : bool, default False
            Sort columns if the columns of `self` and `other` are not aligned.
        '''
        if isinstance(dtypes, dict):
            self._dtypes = pd.Series(dtypes, dtype='object')
        else:
            self._dtypes = dtypes

        if df is None:
            df = pd.DataFrame()
        elif dtypes is None:  # df, no dtypes
            self._dtypes = df.dtypes
            if infer_categories:
                self._infer_and_merge(df)  # sets self._dtypes
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
        self._middles = []
        self._infer_categories = infer_categories
        self._append_kwargs = append_kwargs
        for key in append_kwargs:
            if key not in {'ignore_index', 'verify_integrity', 'sort'}:
                raise ValueError('unexpected kwarg '+key)

    def append(self, other, **kwargs):
        '''Append rows of `other` to the end of the caller.

        Columns in `other` that are not in the caller are added as new columns.

        Unlike pd.DataFrame.append, the caller is modified.

        Unlike Pandas, parameters such as `ignore_index` are not specified
        in the `.append()` call. You should pass them to __init__ instead.

        Parameters
        ----------
        other : DataFrame or Series/dict-like object, or list of these
            The data to append.

        Returns
        -------
        DF_Appender
        '''
        if kwargs:
            raise ValueError('unexpected keyword, should you move it to init()? '+repr(kwargs))

        self._small.append(other)
        if len(self._small) > self._chunksize:
            self._merge_small()
        return self  # mimic pd.DataFrame.append return value

    def finalize(self):
        '''Finalizes all intermediate work and returns a DataFrame.

        Additional `.append()` calls may be made after `.finalize()` is called.
        Frequently calling `finalize` will inhibit pandas-appender from being
        able to save cpu time.

        Returns
        -------
        DataFrame
        '''
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

        self._chunksize = int(self._chunksize * 1.02)

        df = df.append(self._small, **self._append_kwargs)

        if self._infer_categories:
            self._infer_and_merge(df)

        if self._dtypes is not None:
            df = df.astype(self._dtypes)

        self._middles.append(df)
        self._small = []

    def _merge_middles(self):
        if not self._middles:
            return
        self._df = pd.concat((self._df, *self._middles), **self._append_kwargs)
        self._middles = []
