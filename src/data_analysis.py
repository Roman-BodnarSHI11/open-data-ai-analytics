"""Аналіз якості даних для завантажених CSV-датасетів."""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

from constants import DOWNLOADS_FOLDER


def load_csv(path: Path) -> pd.DataFrame | None:
    for enc in ("utf-8", "utf-8-sig", "windows-1251", "latin-1"):
        for sep in (",", ";", "\t"):
            try:
                df = pd.read_csv(path, encoding=enc, sep=sep, low_memory=False)
                if df.shape[1] > 1:
                    print(f"  Кодування: {enc} | Роздільник: '{sep}'")
                    return df
            except Exception:
                continue
    return None


def str_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if df[c].dtype == object or str(df[c].dtype) == "str"]


def analyze(path: Path) -> None:
    print(f"\n{'='*60}\n  {path.name}\n{'='*60}")
    df = load_csv(path)
    if df is None:
        print("  [!] Не вдалося завантажити файл.")
        return

    # Загальна інформація
    print(f"\n[Загальне]  рядків={len(df):,}  колонок={len(df.columns)}")
    print(f"  Колонки: {list(df.columns)}")

    # Пропущені значення
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("\n[Пропущені]  ✓ відсутні")
    else:
        print("\n[Пропущені]")
        for col, n in missing.items():
            print(f"  {col}: {n:,} ({n/len(df)*100:.1f}%)")

    # Дублікати
    full_dups = df.duplicated().sum()
    print(f"\n[Дублікати]  повних рядків: {full_dups:,} ({full_dups/len(df)*100:.1f}%)")

    # Типи та унікальні
    print("\n[Типи даних]")
    for col in df.columns:
        print(f"  {col:<35} {str(df[col].dtype):<10} унікальних: {df[col].nunique():,}")

    # Числова статистика + викиди
    num = df.select_dtypes(include=np.number)
    if not num.empty:
        print("\n[Числові колонки]")
        for col in num.columns:
            s = df[col].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            outliers = int(((s < q1 - 1.5*iqr) | (s > q3 + 1.5*iqr)).sum()) if iqr else 0
            print(f"  {col:<35} min={s.min():.2f}  max={s.max():.2f}  mean={s.mean():.2f}  викидів={outliers}")

    # Аномалії тексту
    issues = []
    for col in str_cols(df):
        s = df[col].dropna()
        ws = int((s.str.strip() == "").sum())
        lt = int((s != s.str.strip()).sum())
        rc = s.nunique() - s.str.lower().nunique()
        if ws: issues.append(f"  {col}: тільки пробіли={ws}")
        if lt: issues.append(f"  {col}: зайві пробіли={lt}")
        if rc > 0: issues.append(f"  {col}: дублікати через регістр={rc}")
    if issues:
        print("\n[Аномалії тексту]")
        print("\n".join(issues))
    else:
        print("\n[Аномалії тексту]  ✓ не знайдено")

    # Бал якості
    score = 100.0
    miss_pct = missing.sum() / df.size * 100 if not missing.empty else 0
    score -= min(30, miss_pct * 3)
    score -= min(20, full_dups / len(df) * 100 * 2)
    score -= min(20, len(issues) * 2)
    grade = "ВІДМІННО" if score >= 90 else "ДОБРЕ" if score >= 70 else "ЗАДОВІЛЬНО" if score >= 50 else "ПОГАНО"
    print(f"\n[Якість]  {score:.0f}/100  {grade}\n")


def main() -> None:
    if len(sys.argv) > 1:
        files = [Path(sys.argv[1])]
    else:
        root = Path(DOWNLOADS_FOLDER)
        files = sorted(root.rglob("*.csv")) if root.exists() else []

    if not files:
        print("Файли не знайдені.")
        return

    for path in files:
        analyze(path)


if __name__ == "__main__":
    main()