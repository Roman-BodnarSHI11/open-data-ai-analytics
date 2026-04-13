"""Flask-додаток: таблиці БД, метадані пайплайну, посилання на звіти та графіки."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, abort, render_template, send_from_directory, url_for
from sqlalchemy import create_engine, text

from constants import REPORTS_DIR
from data_load.db_import import database_url_from_env, normalize_docker_database_url

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)


def _engine():
    return create_engine(normalize_docker_database_url(database_url_from_env()))


@app.route("/")
def index():
    meta_rows = []
    tables = []
    try:
        with _engine().connect() as conn:
            tables = [
                r[0]
                for r in conn.execute(
                    text(
                        """
                        SELECT tablename
                        FROM pg_tables
                        WHERE schemaname = 'public'
                        ORDER BY tablename
                        """
                    )
                ).fetchall()
            ]
            if "pipeline_meta" in tables:
                meta_rows = conn.execute(
                    text(
                        "SELECT source_file, table_name, row_count, created_at "
                        "FROM pipeline_meta ORDER BY id DESC LIMIT 50"
                    )
                ).mappings().all()
    except Exception as exc:
        return render_template("index.html", error=str(exc), tables=[], meta_rows=[])

    reports_root = Path(REPORTS_DIR)
    artifacts = {
        "quality": _safe_list(reports_root / "quality"),
        "research": _safe_list(reports_root / "research"),
        "figures": _safe_list(reports_root / "figures"),
    }
    return render_template(
        "index.html",
        error=None,
        tables=tables,
        meta_rows=meta_rows,
        artifacts=artifacts,
    )


def _safe_list(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_file())


@app.route("/files/<kind>/<path:name>")
def download_artifact(kind: str, name: str):
    if kind not in ("quality", "research", "figures"):
        abort(404)
    if ".." in name or name.startswith("/"):
        abort(404)
    base = Path(REPORTS_DIR) / kind
    return send_from_directory(base, name, as_attachment=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
