# qlib/data/processing/qaqc/anomaly.py
import numpy as np
import pandas as pd
from .base import Strategy

class AnomalyDetector(Strategy):
    """
    Detect and optionally fix/drop anomalies.
    - price_jump_threshold: relative change threshold for close vs prev (e.g. 0.5 = 50%)
    - volume_spike_factor: multiplier vs median
    - mode: 'flag' / 'clip' / 'drop'
    Returns df with 'qaqc_anomaly' boolean column if mode == 'flag'
    """
    def __init__(self, price_jump_threshold=0.5, volume_spike_factor=10.0, mode='flag'):
        self.price_jump_threshold = price_jump_threshold
        self.volume_spike_factor = volume_spike_factor
        assert mode in ('flag','clip','drop')
        self.mode = mode

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'close' not in df.columns:
            return df
        prev = df['close'].shift(1)
        # avoid division by zero
        denom = prev.replace(0, np.nan).abs()
        rel_change = (df['close'] - prev).abs() / denom
        price_idx = rel_change > self.price_jump_threshold

        vol_idx = pd.Series([False]*len(df), index=df.index)
        if 'volume' in df.columns:
            median_vol = df['volume'].median(skipna=True)
            if pd.notna(median_vol) and median_vol > 0:
                vol_idx = df['volume'] > (median_vol * self.volume_spike_factor)

        anomaly_idx = price_idx | vol_idx

        if self.mode == 'flag':
            df['qaqc_anomaly'] = anomaly_idx
        elif self.mode == 'clip':
            # clip close to prev*(1+threshold)
            up = prev * (1 + self.price_jump_threshold)
            down = prev * (1 - self.price_jump_threshold)
            df.loc[price_idx, 'close'] = np.minimum(np.maximum(df.loc[price_idx, 'close'], down[price_idx]), up[price_idx])
            if 'volume' in df.columns:
                df.loc[vol_idx, 'volume'] = median_vol * self.volume_spike_factor
        elif self.mode == 'drop':
            df = df.loc[~anomaly_idx]
        return df

