"""Пайплайн дослідження: вибірки з БД і зведений Markdown-звіт."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from constants import REPORTS_DIR
from data_load.db_import import database_url_from_env, make_engine, normalize_docker_database_url


def _list_data_tables(conn):
    rows = conn.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename NOT IN ('pipeline_meta')
            ORDER BY tablename
            """
        )
    ).fetchall()
    return [r[0] for r in rows]


def main() -> int:
    db_url = normalize_docker_database_url(database_url_from_env())
    engine = make_engine(db_url)
    out_dir = Path(REPORTS_DIR) / "research"
    out_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = ["# Дослідження даних (з БД)\n"]

    with engine.connect() as conn:
        tables = _list_data_tables(conn)
        if not tables:
            lines.append("_Таблиць у схемі public не знайдено._\n")
            (out_dir / "research_summary.md").write_text("\n".join(lines), encoding="utf-8")
            print("Немає таблиць для аналізу.")
            return 0

        for tbl in tables:
            lines.append(f"## Таблиця `{tbl}`\n")
            try:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar()
                lines.append(f"- Рядків: **{cnt:,}**\n")
                sample = pd.read_sql(text(f'SELECT * FROM "{tbl}" LIMIT 5000'), conn)
                lines.append(f"- Колонок: **{sample.shape[1]}**\n")
                num = sample.select_dtypes(include=["number"])
                if not num.empty and num.shape[1] > 0:
                    desc = num.describe().round(3).to_string()
                    lines.append("\n```\n" + desc + "\n```\n")
            except Exception as e:
                lines.append(f"- Помилка: `{e}`\n")

    out_path = out_dir / "research_summary.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Звіт збережено: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
