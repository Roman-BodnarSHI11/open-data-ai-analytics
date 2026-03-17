"""Tests for src/data_quality_analysis/data_model_analysis.py"""

from pathlib import Path

import pandas as pd
import pytest

from data_quality_analysis.data_model_analysis import eda, load_csv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# load_csv (data_model_analysis variant)
# ---------------------------------------------------------------------------

class TestLoadCsv:
    def test_loads_comma_csv(self, tmp_path):
        p = _write_csv(tmp_path / "d.csv", "a,b,c\n1,2,3\n4,5,6\n")
        df = load_csv(p)
        assert df is not None
        assert len(df.columns) == 3

    def test_loads_semicolon_csv(self, tmp_path):
        p = _write_csv(tmp_path / "d.csv", "x;y;z\n1;2;3\n")
        df = load_csv(p)
        assert df is not None
        assert len(df.columns) == 3

    def test_returns_none_for_single_column(self, tmp_path):
        p = _write_csv(tmp_path / "d.csv", "single\n1\n2\n")
        assert load_csv(p) is None


# ---------------------------------------------------------------------------
# eda
# ---------------------------------------------------------------------------

class TestEda:
    def test_runs_on_numeric_csv(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "d.csv", "a,b,c\n1,2,3\n4,5,6\n7,8,9\n")
        eda(p)
        out = capsys.readouterr().out
        assert "Рядків" in out

    def test_reports_dtype_info(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "d.csv", "a,b\n1,2\n3,4\n")
        eda(p)
        out = capsys.readouterr().out
        assert "int" in out or "float" in out

    def test_shows_numeric_describe(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "d.csv", "x,y\n10,100\n20,200\n30,300\n")
        eda(p)
        out = capsys.readouterr().out
        assert "Числова статистика" in out

    def test_shows_categorical_top_values(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "d.csv", "city,score\nKyiv,10\nLviv,20\nKyiv,30\n")
        eda(p)
        out = capsys.readouterr().out
        assert "Категоріальні" in out

    def test_handles_unloadable_file(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "bad.csv", "single\n1\n2\n")
        eda(p)
        out = capsys.readouterr().out
        assert "Не вдалося завантажити" in out

    def test_shows_correlation_for_multi_numeric(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "d.csv", "a,b,c\n1,2,3\n4,5,6\n7,8,9\n")
        eda(p)
        out = capsys.readouterr().out
        assert "Кореляція" in out
