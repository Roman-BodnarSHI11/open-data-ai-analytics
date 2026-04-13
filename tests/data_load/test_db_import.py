"""Тести для src/data_load/db_import.py"""

from data_load.db_import import _assign_unique_sql_columns, _sql_column_base


class TestSqlColumnBase:
    def test_latin_header(self):
        assert _sql_column_base("Region_Name", 0) == "region_name"

    def test_cyrillic_only_uses_position(self):
        assert _sql_column_base("Область", 3) == "col_3"

    def test_leading_digit_gets_prefix(self):
        assert _sql_column_base("123x", 0).startswith("t_")


class TestAssignUniqueSqlColumns:
    def test_unique_after_cyrillic_headers(self):
        cols = ["Область", "Місто", "Тип"]
        out = _assign_unique_sql_columns(cols)
        assert len(out) == len(set(out))
        assert out[0] == "col_0"
        assert out[1] == "col_1"
        assert out[2] == "col_2"

    def test_duplicate_latin_gets_suffix(self):
        out = _assign_unique_sql_columns(["id", "id", "id"])
        assert out[0] == "id"
        assert out[1] == "id_1"
        assert out[2] == "id_2"
