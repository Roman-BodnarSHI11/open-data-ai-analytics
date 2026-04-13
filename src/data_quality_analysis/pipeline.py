"""Пайплайн якості даних: аналіз CSV і збереження JSON-звіту на спільний том."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from constants import DOWNLOADS_FOLDER, REPORTS_DIR
from data_quality_analysis.data_analysis import load_csv


def _score_dataframe(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    full_dups = int(df.duplicated().sum())
    miss_pct = float(missing.sum() / df.size * 100) if not missing.empty else 0.0
    score = 100.0
    score -= min(30, miss_pct * 3)
    score -= min(20, (full_dups / len(df) * 100 * 2) if len(df) else 0)
    return round(score, 1), int(missing.sum()), full_dups


def main() -> int:
    root = Path(DOWNLOADS_FOLDER)
    files = sorted(root.rglob("*.csv")) if root.exists() else []
    if not files:
        print("CSV не знайдені в", root)
        return 1

    out_dir = Path(REPORTS_DIR) / "quality"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {"files": []}
    for path in files:
        df = load_csv(path)
        if df is None:
            report["files"].append({"path": str(path), "error": "read_failed"})
            continue
        score, miss_cells, dups = _score_dataframe(df)
        entry = {
            "path": str(path),
            "name": path.name,
            "rows": int(len(df)),
            "columns": list(map(str, df.columns)),
            "quality_score": score,
            "missing_cells": miss_cells,
            "duplicate_rows": dups,
        }
        report["files"].append(entry)
        print(f"  {path.name}: score={score}")

    out_path = out_dir / "quality_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Звіт збережено: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
