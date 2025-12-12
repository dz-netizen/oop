# quality.py
import pandas as pd
import numpy as np

class DataQualityReport:
    """
    Compute per-instrument quality metrics:
      - missing_rate: fraction of rows with any NaN
      - col_missing_rate: per-column missing rate
      - anomaly_rate: fraction flagged (if 'qaqc_anomaly' present)
      - completeness_score: weighted score (1 - missing_rate)
    """
    def __init__(self):
        pass

    def report(self, df):
        total = len(df)
        if total == 0:
            return {
                "total_rows": 0,
                "missing_rate": 1.0,
                "completeness": 0.0,
                "anomaly_rate": None,
                "col_missing_rate": {}
            }
        row_missing = df.isna().any(axis=1).sum()
        missing_rate = row_missing / total
        col_missing = df.isna().mean().to_dict()
        anomaly_rate = None
        if 'qaqc_anomaly' in df.columns:
            anomaly_rate = df['qaqc_anomaly'].sum() / total
        completeness = max(0.0, 1.0 - missing_rate)
        return {
            "total_rows": int(total),
            "missing_rate": float(missing_rate),
            "completeness": float(completeness),
            "anomaly_rate": (float(anomaly_rate) if anomaly_rate is not None else None),
            "col_missing_rate": {k: float(v) for k,v in col_missing.items()}
        }

