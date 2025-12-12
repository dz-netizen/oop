# cleaner.py
import pandas as pd
from typing import List, Optional, Dict, Tuple

from .base import QAQCCleanerBase
from .align_calendar import AlignCalendar
from .ohlc_strategies import ForwardFillOHLC, PrevCloseOHLC, InterpolateOHLC, DropMissingOHLC
from .volume_strategies import ZeroVolume, MeanVolume, FFillVolume
from .anomaly import AnomalyDetector
from .quality import DataQualityReport

class CNDataCleaner(QAQCCleanerBase):
    """
    High-level cleaner:
      - trading_calendar: index to align to
      - ohlc_strategy: 'ffill'/'prev_close'/'interpolate'/'drop'/'keep_na'
      - volume_strategy: 'zero'/'mean'/'ffill'/'keep_na'
      - anomaly_cfg: dict or None, e.g. {'price_jump_threshold':0.5,'volume_spike_factor':10,'mode':'flag'}
      - missing_threshold: if instrument missing_rate > threshold then the instrument will be flagged/dropped externally
      - report: whether to return quality report
    """

    def __init__(
        self,
        trading_calendar,
        ohlc_strategy: str = 'ffill',
        volume_strategy: str = 'zero',
        anomaly_cfg: Optional[Dict] = None,
        missing_threshold: float = 0.3,
        report: bool = True
    ):
        self.calendar = pd.to_datetime(trading_calendar)
        self.ohlc_strategy = ohlc_strategy
        self.volume_strategy = volume_strategy
        self.anomaly_cfg = anomaly_cfg
        self.missing_threshold = missing_threshold
        self.report = report
        self.qualityer = DataQualityReport()

    def _build_ohlc_strategy(self):
        s = self.ohlc_strategy
        if s == 'ffill':
            return ForwardFillOHLC()
        if s == 'prev_close':
            return PrevCloseOHLC()
        if s == 'interpolate':
            return InterpolateOHLC()
        if s == 'drop':
            return DropMissingOHLC()
        return None

    def _build_volume_strategy(self):
        s = self.volume_strategy
        if s == 'zero':
            return ZeroVolume()
        if s == 'mean':
            return MeanVolume()
        if s == 'ffill':
            return FFillVolume()
        return None

    def clean_one(self, df: pd.DataFrame, instrument: Optional[str]=None) -> Tuple[Optional[pd.DataFrame], Dict]:
        """
        Clean a single instrument's DataFrame.
        Returns (cleaned_df_or_None_if_dropped, info_dict)
        info_dict contains keys: missing_rate, dropped(bool), quality_report(dict)
        """
        info = {"instrument": instrument}
        # 0. align calendar
        df = AlignCalendar(self.calendar).apply(df)

        # 1. OHLC strategy
        ohlc_s = self._build_ohlc_strategy()
        if ohlc_s is not None:
            df = ohlc_s.apply(df)

        # 2. Volume strategy
        vol_s = self._build_volume_strategy()
        if vol_s is not None:
            df = vol_s.apply(df)

        # 3. anomaly detection
        if self.anomaly_cfg:
            detector = AnomalyDetector(
                price_jump_threshold=self.anomaly_cfg.get('price_jump_threshold', 0.5),
                volume_spike_factor=self.anomaly_cfg.get('volume_spike_factor', 10.0),
                mode=self.anomaly_cfg.get('mode', 'flag')
            )
            df = detector.apply(df)

        # 4. compute quality
        quality = self.qualityer.report(df)
        info['quality'] = quality

        # 5. missing threshold decision
        dropped = False
        if quality['missing_rate'] > self.missing_threshold:
            # we choose to drop instrument: return None; user can decide alternatively to mark
            dropped = True
            info['dropped'] = True
            info['reason'] = 'missing_threshold_exceeded'
            return None, info

        info['dropped'] = False
        return df, info

    def clean_many(self, data_dict: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Dict]]:
        """
        data_dict: mapping instrument -> DataFrame
        returns (cleaned_dict, info_dict)
        """
        cleaned = {}
        infos = {}
        for inst, df in data_dict.items():
            c_df, info = self.clean_one(df.copy(), instrument=inst)
            infos[inst] = info
            if c_df is not None:
                cleaned[inst] = c_df
        return cleaned, infos

