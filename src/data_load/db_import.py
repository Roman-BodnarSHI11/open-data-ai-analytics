"""Імпорт CSV у PostgreSQL: читання файлу, створення таблиці, завантаження рядків."""

from __future__ import annotations

import re
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def _sanitize_table_name(name: str, max_len: int = 60) -> str:
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", name).strip("_").lower()
    if not s or s[0].isdigit():
        s = "t_" + s
    return s[:max_len] or "imported_data"


def _sql_column_base(raw: str, position: int, max_len: int = 63) -> str:
    """Лише латиниця/цифри/_; кирилиця дає порожній рядок — тоді col_<n>."""
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", str(raw)).strip("_").lower()
    if not s:
        return f"col_{position}"[:max_len]
    if s[0].isdigit():
        s = ("t_" + s)[:max_len]
    return (s[:max_len] or f"col_{position}")[:max_len]


def _assign_unique_sql_columns(raw_columns: list[str], max_len: int = 63) -> list[str]:
    """Унікальні імена колонок для SQL (без DuplicateColumnError)."""
    bases = [_sql_column_base(c, i, max_len) for i, c in enumerate(raw_columns)]
    result: list[str] = []
    used: set[str] = set()
    for stem in bases:
        stem = stem or "col"
        candidate = stem[:max_len]
        k = 0
        while candidate in used:
            k += 1
            suffix = f"_{k}"
            allowed = max(1, max_len - len(suffix))
            candidate = (stem[:allowed] + suffix)[:max_len]
        used.add(candidate)
        result.append(candidate)
    return result


def _load_csv(path: Path) -> pd.DataFrame | None:
    for enc in ("utf-8", "utf-8-sig", "windows-1251", "latin-1"):
        for sep in (",", ";", "\t"):
            try:
                df = pd.read_csv(path, encoding=enc, sep=sep, low_memory=False)
                if df.shape[1] > 1:
                    return df
            except Exception:
                continue
    return None


def make_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def import_csv_to_db(
    engine: Engine,
    csv_path: Path,
    table_name: str | None = None,
    if_exists: str = "replace",
    chunksize: int = 5000,
) -> str:
    """
    Зчитує CSV, створює таблицю (replace/append) і імпортує дані.

    Повертає фактичне ім'я таблиці в БД.
    """
    df = _load_csv(csv_path)
    if df is None:
        raise ValueError(f"Не вдалося прочитати CSV: {csv_path}")

    tbl = table_name or _sanitize_table_name(csv_path.stem)
    df.columns = _assign_unique_sql_columns(list(df.columns))

    with engine.begin() as conn:
        df.to_sql(
            tbl,
            conn,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=chunksize,
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS pipeline_meta (
                    id SERIAL PRIMARY KEY,
                    source_file TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        )
        conn.execute(
            text(
                "INSERT INTO pipeline_meta (source_file, table_name, row_count) "
                "VALUES (:src, :tbl, :rc)"
            ),
            {"src": str(csv_path), "tbl": tbl, "rc": int(len(df))},
        )
    return tbl


def import_all_csv_in_dir(engine: Engine, directory: Path) -> list[tuple[Path, str]]:
    """Імпортує всі *.csv у каталозі (рекурсивно). Повертає список (шлях, таблиця)."""
    if not directory.exists():
        return []
    results: list[tuple[Path, str]] = []
    for path in sorted(directory.rglob("*.csv")):
        tbl = _sanitize_table_name(path.stem + "_" + path.parent.name[:20])
        tbl = import_csv_to_db(engine, path, table_name=tbl, if_exists="replace")
        results.append((path, tbl))
    return results


def database_url_from_env() -> str:
    import os

    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "analytics")
    password = os.environ.get("POSTGRES_PASSWORD", "analytics")
    db = os.environ.get("POSTGRES_DB", "analytics")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def normalize_docker_database_url(url: str) -> str:
    """docker-compose інколи передає postgres:// — конвертуємо для SQLAlchemy."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url
