import warnings

import pandas as pd


from . import hints


class DF_Appender(object):
    '''A class used to make appending to a Pandas DataFrame efficient.'''

    def __init__(self, data=None, chunksize=5000, dtypes=None, infer_categories=False, verbose=0, **extra_kwargs):
        '''Initialize a DF_Appender object.

        Parameters
        ----------
        data : DataFrame or Series/dict-like object, or list of these
            Initialize the DF_Appender with this data.
        chunksize : int, default 5000
            `chunksize` controls how much extra memory the append algorithm
            uses in order to save cpu time.
        dtypes : str, type, dict, default None
            Initialize the DataFrame with these column dtypes.
        infer_categories : bool, default False
            If True, examine the first chunk of appended rows to determine
            which columns are smaler as dtype 'category'.
        verbose : int, default 0
            If not zero, be verbose.
        ignore_index : bool, default False
            If True, the resulting axis will be labeled 0, 1, …, n - 1.
        verify_integrity : bool, default False
            If True, raise ValueError on creating index with duplicates.
        sort : bool, default False
            Sort columns if the columns of `self` and `other` are not aligned.
        '''
        self.chunksize = chunksize
        self.small = []
        self.middles = []
        self.infer_categories = infer_categories
        self.inferred_categories = None
        self.verbose = verbose
        for key in extra_kwargs:
            if key not in {'ignore_index', 'verify_integrity', 'sort'}:
                raise ValueError('unexpected kwarg '+key)
        self.extra_kwargs = extra_kwargs

        if isinstance(dtypes, dict):
            # convert to a Pandas dtypes
            self.explicit_dtypes = pd.Series(dtypes, dtype='object')
        else:
            self.explicit_dtypes = dtypes  # could be None

        # if data is a DataFrame, can't use it as a bool
        self.df = pd.DataFrame()
        try:
            if data:
                self.df = pd.DataFrame(data, copy=True)
        except ValueError:
            # data was a df
            self.df = data.copy()

        if self.explicit_dtypes is not None and not self.df.empty:
            self.df = self.df.astype(self.explicit_dtypes)

    def append(self, other, **kwargs):
        '''Append row(s) of `other` to the end of the caller. `other` can be
        anything you would pass to a pd.DataFrame constructor.

        Columns in `other` that are not already in the caller are added as new columns.

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

        self.small.append(other)
        if len(self.small) > self.chunksize:
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
        return self.df

    def _merge_small(self):
        if not self.small:
            # no work to do
            return
        self.chunksize = int(self.chunksize * 1.02)

        # use the DataFrame constructor because it is good at merging types
        small_df = pd.DataFrame(self.small)  # does not have a dtypes= kwarg
        self.small  = []
        if self.explicit_dtypes is not None:
            small_df = small_df.astype(self.explicit_dtypes)

        if self.infer_categories:
            if self.verbose > 1:
                print('inferring categories', file=sys.stderr)
            df_cats = hints.infer_categories(self.df, verbose=self.verbose)
            small_cats = hints.infer_categories(small_df, verbose=self.verbose)

            if not df_cats.equals(small_cats):  # pd.Series
                df_size = self.df.memory_usage(index=False, deep=True).sum()
                small_size = small_df.memory_usage(index=False, deep=True).sum()
                cats = df_cats if df_size > small_size else small_cats
            else:
                cats = df_cats
            if self.verbose:
                print('inferred cats: ', ','.join(cats.keys()), file=sys.stderr)
            self.inferred_categories = cats

            if not self.df.empty:
                self.df = self.df.astype(hints.infer_to_dtypes(cats, self.df.dtypes))
            small_df = small_df.astype(hints.infer_to_dtypes(cats, small_df.dtypes))

        elif self.inferred_categories:
            small_df = small_df.astype(hints.infer_to_dtypes(self.inferred_categories, small_df.dtypes))

        self.middles.append(small_df)


    def _merge_middles(self):
        if not self.middles:
            return

        self.middles.insert(0, self.df)

        if self.explicit_dtypes is not None:
            self.df = pd.concat(self.middles, **self.extra_kwargs)
            self.middles = []
            return

        dtypes = hints.harmonize_types(self.middles, verbose=self.verbose)
        dfs = []
        for _ in range(len(self.middles)):
            df = self.middles.pop(0)
            df = df.astype(dtypes) if dtypes else df
            dfs.append(df)
        self.df = pd.concat(dfs, **self.extra_kwargs)
