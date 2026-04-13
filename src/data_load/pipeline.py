"""Контейнерний пайплайн: завантаження датасетів і імпорт CSV у БД."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from constants import DATASETS_URLS, DOWNLOADS_FOLDER
from data_load.db_import import (
    database_url_from_env,
    import_all_csv_in_dir,
    make_engine,
    normalize_docker_database_url,
)
from data_load.data_set import download_dataset


def main() -> int:
    skip_download = os.environ.get("SKIP_DOWNLOAD", "").lower() in ("1", "true", "yes")
    data_dir = Path(DOWNLOADS_FOLDER)
    data_dir.mkdir(parents=True, exist_ok=True)

    if not skip_download:
        print("=== Завантаження датасетів (CKAN) ===")
        for url in DATASETS_URLS:
            print(f"\nURL: {url}")
            download_dataset(url, output_folder=str(data_dir))
    else:
        print("=== SKIP_DOWNLOAD=1 — використовуємо наявні CSV у томі ===")

    db_url = normalize_docker_database_url(database_url_from_env())
    print(f"\n=== Імпорт CSV у PostgreSQL ===\n  DSN host: {db_url.split('@')[-1] if '@' in db_url else db_url[:40]}")

    engine = make_engine(db_url)
    imported = import_all_csv_in_dir(engine, data_dir)
    if not imported:
        print("  Немає CSV для імпорту в", data_dir.resolve())
        return 1

    for p, tbl in imported:
        print(f"  OK  {p.name}  ->  public.{tbl}")
    print(f"\n=== Імпортовано файлів: {len(imported)} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
