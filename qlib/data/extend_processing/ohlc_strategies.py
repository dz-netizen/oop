# ohlc_strategies.py
import pandas as pd
from .base import Strategy

class ForwardFillOHLC(Strategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = ['open','high','low','close']
        for c in cols:
            if c in df.columns:
                df[c] = df[c].ffill()
        return df

class PrevCloseOHLC(Strategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # fill close by previous day's close, leave other OHLC as-is
        if 'close' in df.columns:
            df['close'] = df['close'].fillna(method=None)  # ensure NaNs present
            df['close'] = df['close'].mask(df['close'].isna(), df['close'].shift(1))
        return df

class InterpolateOHLC(Strategy):
    def __init__(self, method='linear', limit=None):
        self.method = method
        self.limit = limit

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = ['open','high','low','close']
        existing = [c for c in cols if c in df.columns]
        if existing:
            df[existing] = df[existing].interpolate(method=self.method, limit=self.limit)
        return df

class DropMissingOHLC(Strategy):
    def __init__(self, subset=None):
        self.subset = subset or ['close']

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(subset=self.subset)

