# align_calendar.py
import pandas as pd
from .base import Strategy

class AlignCalendar(Strategy):
    """Reindex to trading calendar (DatetimeIndex)."""
    def __init__(self, calendar):
        # calendar: pd.DatetimeIndex or list-like
        self.calendar = pd.to_datetime(calendar)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # keep columns as-is, reindex rows (dates)
        return df.reindex(self.calendar)

