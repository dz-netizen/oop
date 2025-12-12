# use_example.py
import pandas as pd
from qlib.data.processing.qaqc.cleaner import CNDataCleaner

# sample trading calendar
calendar = pd.date_range("2025-01-01", "2025-01-15", freq='B')

# simulate raw per-instrument DataFrame (sparse dates)
raw_df = pd.DataFrame({
    "open":[10, 11, None, 13],
    "high":[10.2, 11.3, None, 13.5],
    "low":[9.5, 10.8, None, 12.7],
    "close":[10.0, 11.0, None, 13.0],
    "volume":[1000, 1200, None, 1500]
}, index=pd.to_datetime(['2025-01-02','2025-01-03','2025-01-08','2025-01-09']))

cleaner = CNDataCleaner(
    trading_calendar=calendar,
    ohlc_strategy='interpolate',
    volume_strategy='mean',
    anomaly_cfg={'price_jump_threshold':0.4,'volume_spike_factor':8.0,'mode':'flag'},
    missing_threshold=0.4,
    report=True
)
cleaned_df, info = cleaner.clean_one(raw_df, instrument='000001.SZ')
print("info:", info)
print(cleaned_df.head())

