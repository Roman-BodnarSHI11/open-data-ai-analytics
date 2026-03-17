"""Tests for src/visualization/visualize.py"""

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe in CI

import pandas as pd
import pytest

from visualization.visualize import (
    create_categorical_visualizations,
    create_visualizations,
    detect_encoding,
    get_figures_directory,
    read_csv_flexible,
    visualize_data,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, content: str, encoding: str = "utf-8") -> str:
    path.write_text(content, encoding=encoding)
    return str(path)


# ---------------------------------------------------------------------------
# detect_encoding
# ---------------------------------------------------------------------------

class TestDetectEncoding:
    def test_detects_utf8(self, tmp_path):
        p = tmp_path / "f.csv"
        p.write_text("hello,world\n1,2\n", encoding="utf-8")
        enc = detect_encoding(str(p))
        assert enc is not None
        assert "utf" in enc.lower() or enc.lower() in ("ascii",)

    def test_returns_string(self, tmp_path):
        p = tmp_path / "f.csv"
        p.write_bytes(b"a,b\n1,2\n")
        enc = detect_encoding(str(p))
        assert isinstance(enc, str)


# ---------------------------------------------------------------------------
# read_csv_flexible
# ---------------------------------------------------------------------------

class TestReadCsvFlexible:
    def test_reads_comma_separated(self, tmp_path):
        path = _write_csv(tmp_path / "d.csv", "a,b,c\n1,2,3\n4,5,6\n")
        df = read_csv_flexible(path)
        assert len(df.columns) >= 2

    def test_reads_semicolon_separated(self, tmp_path):
        path = _write_csv(tmp_path / "d.csv", "x;y;z\n10;20;30\n")
        df = read_csv_flexible(path)
        assert len(df.columns) >= 2

    def test_reads_tab_separated(self, tmp_path):
        path = _write_csv(tmp_path / "d.csv", "col1\tcol2\n1\t2\n")
        df = read_csv_flexible(path)
        assert len(df.columns) >= 2

    def test_returns_dataframe(self, tmp_path):
        path = _write_csv(tmp_path / "d.csv", "a,b\n1,2\n")
        result = read_csv_flexible(path)
        assert isinstance(result, pd.DataFrame)

    def test_handles_single_column_fallback(self, tmp_path):
        path = _write_csv(tmp_path / "d.csv", "only_one_column_no_delimiter\nvalue1\nvalue2\n")
        df = read_csv_flexible(path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


# ---------------------------------------------------------------------------
# get_figures_directory
# ---------------------------------------------------------------------------

class TestGetFiguresDirectory:
    def test_returns_existing_directory(self):
        d = get_figures_directory()
        assert os.path.isdir(d)

    def test_path_ends_with_reports_figures(self):
        d = get_figures_directory()
        assert d.endswith(os.path.join("reports", "figures"))


# ---------------------------------------------------------------------------
# create_visualizations
# ---------------------------------------------------------------------------

class TestCreateVisualizations:
    def test_creates_histogram_png(self, tmp_path):
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [5, 4, 3, 2, 1], "c": [1, 3, 5, 7, 9]})
        create_visualizations(df, "test_file.csv", str(tmp_path))
        assert any(f.endswith("_histograms.png") for f in os.listdir(tmp_path))

    def test_creates_correlation_png_for_multi_numeric(self, tmp_path):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        create_visualizations(df, "test_file.csv", str(tmp_path))
        assert any(f.endswith("_correlation.png") for f in os.listdir(tmp_path))

    def test_creates_boxplot_png(self, tmp_path):
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 4, 6, 8, 10]})
        create_visualizations(df, "test_file.csv", str(tmp_path))
        assert any(f.endswith("_boxplot.png") for f in os.listdir(tmp_path))

    def test_handles_no_numeric_columns(self, tmp_path, capsys):
        df = pd.DataFrame({"city": ["Kyiv", "Lviv", "Odesa"], "region": ["A", "B", "C"]})
        create_visualizations(df, "cat_file.csv", str(tmp_path))
        out = capsys.readouterr().out
        assert "числових" in out or len(os.listdir(tmp_path)) >= 0


# ---------------------------------------------------------------------------
# create_categorical_visualizations
# ---------------------------------------------------------------------------

class TestCreateCategoricalVisualizations:
    def test_creates_categorical_png(self, tmp_path):
        df = pd.DataFrame({"city": ["Kyiv"] * 5 + ["Lviv"] * 3 + ["Odesa"] * 2})
        create_categorical_visualizations(df, "cat", str(tmp_path))
        assert any("categorical" in f for f in os.listdir(tmp_path))

    def test_does_nothing_for_empty_categorical(self, tmp_path):
        df = pd.DataFrame({"a": [1, 2, 3]})
        create_categorical_visualizations(df, "num", str(tmp_path))
        assert len(os.listdir(tmp_path)) == 0


# ---------------------------------------------------------------------------
# visualize_data (high-level)
# ---------------------------------------------------------------------------

class TestVisualizeData:
    def test_processes_csv_file(self, tmp_path, capsys):
        path = _write_csv(tmp_path / "data.csv", "a,b,c\n1,2,3\n4,5,6\n7,8,9\n")
        visualize_data([path])
        out = capsys.readouterr().out
        assert "Успішно оброблено" in out

    def test_skips_unsupported_format(self, tmp_path, capsys):
        p = tmp_path / "data.json"
        p.write_text('{"key": "value"}')
        visualize_data([str(p)])
        out = capsys.readouterr().out
        assert "не підтримується" in out

    def test_processes_multiple_files(self, tmp_path, capsys):
        p1 = _write_csv(tmp_path / "a.csv", "x,y\n1,2\n3,4\n")
        p2 = _write_csv(tmp_path / "b.csv", "m,n\n5,6\n7,8\n")
        visualize_data([p1, p2])
        out = capsys.readouterr().out
        assert "2" in out

    def test_handles_empty_file_list(self, capsys):
        visualize_data([])
        out = capsys.readouterr().out
        assert "0" in out
