import sys
from pathlib import Path

import pandas as pd

from constants import DOWNLOADS_FOLDER


def load_csv(path: Path) -> pd.DataFrame | None:
    for enc in ("utf-8", "utf-8-sig", "windows-1251", "latin-1"):
        for sep in (",", ";", "\t"):
            try:
                df = pd.read_csv(path, encoding=enc, sep=sep, low_memory=False)
                if df.shape[1] > 1:
                    return df
            except Exception:
                continue
    return None


def eda(path: Path) -> None:
    df = load_csv(path)
    if df is None:
        print(f"[!] Не вдалося завантажити: {path}")
        return

    print(f"\n{'='*55}  {path.name}")

    # Форма та типи
    print(f"\nРядків: {len(df):,}  |  Колонок: {len(df.columns)}")
    print(df.dtypes.to_string())

    # Числова статистика
    num = df.select_dtypes("number")
    if not num.empty:
        print("\n--- Числова статистика ---")
        print(num.describe().round(2).to_string())

    # Категоріальні колонки — топ-3 значення
    cat_cols = [c for c in df.columns if str(df[c].dtype) in ("object", "str")]
    if cat_cols:
        print("\n--- Категоріальні колонки (топ-3) ---")
        for col in cat_cols:
            top = df[col].value_counts().head(3)
            print(f"\n  {col}:")
            for val, cnt in top.items():
                print(f"    {str(val)[:40]:<42} {cnt:>6,} ({cnt/len(df)*100:.1f}%)")

    # Кореляція числових
    if num.shape[1] > 1:
        print("\n--- Кореляція ---")
        print(num.corr().round(2).to_string())


def main() -> None:
    files = [Path(sys.argv[1])] if len(sys.argv) > 1 else sorted(Path(DOWNLOADS_FOLDER).rglob("*.csv"))
    if not files:
        print("CSV-файли не знайдені.")
        return
    for f in files:
        eda(f)


if __name__ == "__main__":
    main()