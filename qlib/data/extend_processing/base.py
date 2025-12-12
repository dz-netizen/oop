# base.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Optional, Dict

class Strategy(ABC):
    """Base class for any in-place row/column data strategy."""
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

class QAQCCleanerBase(ABC):
    """
    Base cleaner class. Concrete cleaners should implement `clean_one`
    which processes a single instrument DataFrame and returns (df, info).
    """
    @abstractmethod
    def clean_one(self, df: pd.DataFrame, instrument: Optional[str]=None) -> Tuple[pd.DataFrame, Dict]:
        pass

