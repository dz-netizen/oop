# volume_stragegies.py
import pandas as pd
from .base import Strategy

class ZeroVolume(Strategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0)
        return df

class MeanVolume(Strategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'volume' in df.columns:
            m = df['volume'].mean(skipna=True)
            df['volume'] = df['volume'].fillna(m)
        return df

class FFillVolume(Strategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'volume' in df.columns:
            df['volume'] = df['volume'].ffill()
        return df

