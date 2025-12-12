import os
import fire
import pandas as pd
from pathlib import Path
import ruamel.yaml as yaml

# === 关键：导入你提供的数据清洗模块 ===
from qlib.data.extend_processing import (
    CNDataCleaner,
    AlignCalendar,
    ForwardFillOHLC, PrevCloseOHLC, InterpolateOHLC, DropMissingOHLC,
    ZeroVolume, MeanVolume, FFillVolume,
    AnomalyDetector,
    DataQualityReport,
)

###############################################
# Part 1: 运行你的数据清洗流水线
###############################################
def run_clean_pipeline(raw_df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    print("[qclean] 构建清洗器 CNDataCleaner ...")

    cleaner = CNDataCleaner(
        calendar_align=AlignCalendar(**cfg.get("calendar_align", {})),
        ohlc_strategy={
            "ffill": ForwardFillOHLC,
            "prev_close": PrevCloseOHLC,
            "interp": InterpolateOHLC,
            "drop": DropMissingOHLC,
        }[cfg["ohlc_strategy"]](),
        volume_strategy={
            "zero": ZeroVolume,
            "mean": MeanVolume,
            "ffill": FFillVolume,
        }[cfg["volume_strategy"]](),
        anomaly_detector=AnomalyDetector(**cfg.get("anomaly", {})),
        quality_report=DataQualityReport(),
    )

    print("[qclean] 开始清洗数据 ...")
    cleaned_df = cleaner.clean(raw_df)

    print("[qclean] 数据清洗完成！")
    return cleaned_df


###############################################
# Part 2: 将清洗后的数据写入 Qlib Provider
###############################################
def write_provider(clean_df: pd.DataFrame, out_dir: Path):
    print(f"[qclean] 写入 Qlib provider 目录: {out_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    meta_dir = out_dir / "meta"
    feature_dir = out_dir / "features"
    label_dir = out_dir / "labels"

    meta_dir.mkdir(exist_ok=True)
    feature_dir.mkdir(exist_ok=True)
    label_dir.mkdir(exist_ok=True)

    # —— instruments 列表 ——
    instruments = sorted(clean_df.index.get_level_values("instrument").unique())
    (meta_dir / "instruments.txt").write_text("\n".join(instruments))

    # —— feature/label 列分拆 ——
    feature_cols = [c for c in clean_df.columns if c != "label"]
    label_cols = ["label"] if "label" in clean_df.columns else []

    # —— 分 instrument 写 feather ——
    for inst in instruments:
        inst_df = clean_df.xs(inst, level="instrument")

        inst_df[feature_cols].reset_index().to_feather(feature_dir / f"{inst}.feather")

        if label_cols:
            inst_df[label_cols].reset_index().to_feather(label_dir / f"{inst}.feather")

    print("[qclean] Provider 写入成功！")


###############################################
# Part 3: CLI 入口
###############################################
def run(config_path):
    print(f"[qclean] 加载配置文件: {config_path}")

    with open(config_path, "r") as f:
        cfg = yaml.YAML(typ="safe").load(f)

    qc_cfg = cfg["qclean"]
    parquet_path = os.path.expanduser(qc_cfg["input_parquet"])
    output_dir = Path(os.path.expanduser(qc_cfg["output_provider_dir"]))

    print(f"[qclean] 读取 parquet: {parquet_path}")
    raw_df = pd.read_parquet(parquet_path)

    # 确保 multi-index
    raw_df["datetime"] = pd.to_datetime(raw_df["datetime"])
    raw_df = raw_df.set_index(["datetime", "instrument"]).sort_index()

    # —— 调用你的清洗模块 ——
    cleaned_df = run_clean_pipeline(raw_df, qc_cfg)

    # —— 写 provider ——
    write_provider(cleaned_df, output_dir)

    print("[qclean] 全流程完成！")


def main():
    fire.Fire(run)


if __name__ == "__main__":
    main()
