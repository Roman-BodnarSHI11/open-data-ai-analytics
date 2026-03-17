"""Tests for src/data_quality_analysis/data_analysis.py"""

import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data_quality_analysis.data_analysis import analyze, load_csv, str_cols


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, content: str, encoding: str = "utf-8") -> Path:
    path.write_text(content, encoding=encoding)
    return path


# ---------------------------------------------------------------------------
# load_csv
# ---------------------------------------------------------------------------

class TestLoadCsv:
    def test_reads_comma_separated(self, tmp_path):
        p = _write_csv(tmp_path / "data.csv", "a,b,c\n1,2,3\n4,5,6\n")
        df = load_csv(p)
        assert df is not None
        assert list(df.columns) == ["a", "b", "c"]
        assert len(df) == 2

    def test_reads_semicolon_separated(self, tmp_path):
        p = _write_csv(tmp_path / "data.csv", "x;y;z\n10;20;30\n")
        df = load_csv(p)
        assert df is not None
        assert len(df.columns) == 3

    def test_reads_tab_separated(self, tmp_path):
        p = _write_csv(tmp_path / "data.csv", "col1\tcol2\tcol3\n1\t2\t3\n")
        df = load_csv(p)
        assert df is not None
        assert len(df.columns) == 3

    def test_returns_none_for_single_column_file(self, tmp_path):
        p = _write_csv(tmp_path / "bad.csv", "only_one_column\n1\n2\n")
        result = load_csv(p)
        assert result is None

    def test_reads_windows1251_encoding(self, tmp_path):
        content = "назва,значення\nтест,123\n"
        p = tmp_path / "win.csv"
        p.write_bytes(content.encode("windows-1251"))
        df = load_csv(p)
        assert df is not None
        assert len(df.columns) == 2


# ---------------------------------------------------------------------------
# str_cols
# ---------------------------------------------------------------------------

class TestStrCols:
    def test_returns_only_object_columns(self):
        df = pd.DataFrame({"a": ["x", "y"], "b": [1, 2], "c": ["p", "q"]})
        result = str_cols(df)
        assert set(result) == {"a", "c"}

    def test_returns_empty_for_numeric_only(self):
        df = pd.DataFrame({"x": [1, 2], "y": [3.0, 4.0]})
        assert str_cols(df) == []

    def test_returns_all_for_all_object(self):
        df = pd.DataFrame({"a": ["1"], "b": ["2"], "c": ["3"]})
        assert set(str_cols(df)) == {"a", "b", "c"}


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------

class TestAnalyze:
    def test_runs_without_error_on_valid_csv(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "data.csv", "col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "Якість" in out

    def test_handles_missing_values(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "missing.csv", "a,b,c\n1,,3\n4,5,\n7,8,9\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "Пропущені" in out

    def test_detects_duplicates(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "dup.csv", "a,b\n1,2\n1,2\n3,4\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "Дублікати" in out

    def test_handles_unloadable_file(self, tmp_path, capsys):
        p = tmp_path / "bad.csv"
        p.write_text("only_one_column\n1\n2\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "Не вдалося завантажити" in out

    def test_quality_score_present_in_output(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "clean.csv", "x,y,z\n1,2,3\n4,5,6\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "/100" in out

    def test_detects_text_anomalies_leading_whitespace(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "spaces.csv", "name,value\n Alice,1\nBob ,2\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "Аномалії тексту" in out

    def test_reports_numeric_stats(self, tmp_path, capsys):
        p = _write_csv(tmp_path / "nums.csv", "a,b\n10,100\n20,200\n30,300\n")
        analyze(p)
        out = capsys.readouterr().out
        assert "Числові колонки" in out
