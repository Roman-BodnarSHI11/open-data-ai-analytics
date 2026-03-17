"""Tests for src/data_load/data_set.py"""

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from data_load.data_set import (
    download_dataset,
    download_file,
    extract_dataset_id,
    get_resource_urls,
)


# ---------------------------------------------------------------------------
# extract_dataset_id
# ---------------------------------------------------------------------------

class TestExtractDatasetId:
    VALID_URL = "https://data.gov.ua/dataset/ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb"
    EXPECTED_ID = "ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb"

    def test_extracts_uuid_from_url(self):
        assert extract_dataset_id(self.VALID_URL) == self.EXPECTED_ID

    def test_extracts_uuid_with_trailing_slash(self):
        assert extract_dataset_id(self.VALID_URL + "/") == self.EXPECTED_ID

    def test_raises_on_url_without_uuid(self):
        with pytest.raises(ValueError, match="Не вдалося знайти ID датасету"):
            extract_dataset_id("https://data.gov.ua/dataset/no-uuid-here")

    def test_raises_on_empty_string(self):
        with pytest.raises(ValueError):
            extract_dataset_id("")

    def test_uuid_format_is_valid(self):
        uuid = extract_dataset_id(self.VALID_URL)
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(pattern, uuid)


# ---------------------------------------------------------------------------
# get_resource_urls
# ---------------------------------------------------------------------------

class TestGetResourceUrls:
    DATASET_ID = "ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb"

    def _make_response(self, resources):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "success": True,
            "result": {"resources": resources},
        }
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    @patch("data_load.data_set.requests.get")
    def test_returns_list_of_resource_dicts(self, mock_get):
        mock_get.return_value = self._make_response([
            {"id": "r1", "name": "File 1", "url": "http://example.com/f1.csv", "format": "CSV"},
        ])
        result = get_resource_urls(self.DATASET_ID)
        assert len(result) == 1
        assert result[0]["id"] == "r1"
        assert result[0]["url"] == "http://example.com/f1.csv"
        assert result[0]["format"] == "csv"

    @patch("data_load.data_set.requests.get")
    def test_skips_resources_without_url(self, mock_get):
        mock_get.return_value = self._make_response([
            {"id": "r1", "name": "No URL", "url": "", "format": "CSV"},
            {"id": "r2", "name": "Has URL", "url": "http://example.com/f2.csv", "format": "CSV"},
        ])
        result = get_resource_urls(self.DATASET_ID)
        assert len(result) == 1
        assert result[0]["id"] == "r2"

    @patch("data_load.data_set.requests.get")
    def test_returns_empty_list_when_no_resources(self, mock_get):
        mock_get.return_value = self._make_response([])
        result = get_resource_urls(self.DATASET_ID)
        assert result == []

    @patch("data_load.data_set.requests.get")
    def test_raises_on_api_failure(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"success": False}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        with pytest.raises(RuntimeError, match="CKAN API"):
            get_resource_urls(self.DATASET_ID)

    @patch("data_load.data_set.requests.get")
    def test_uses_resource_id_as_name_fallback(self, mock_get):
        mock_get.return_value = self._make_response([
            {"id": "r1", "url": "http://example.com/f.csv", "format": "CSV"},
        ])
        result = get_resource_urls(self.DATASET_ID)
        assert result[0]["name"] == "r1"


# ---------------------------------------------------------------------------
# download_file
# ---------------------------------------------------------------------------

class TestDownloadFile:
    @patch("data_load.data_set.requests.get")
    def test_creates_file_at_dest(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.raise_for_status = MagicMock()
        mock_resp.iter_content.return_value = [b"hello", b" world"]
        mock_get.return_value = mock_resp

        dest = tmp_path / "subdir" / "file.csv"
        download_file("http://example.com/file.csv", dest)

        assert dest.exists()
        assert dest.read_bytes() == b"hello world"

    @patch("data_load.data_set.requests.get")
    def test_creates_parent_directories(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.raise_for_status = MagicMock()
        mock_resp.iter_content.return_value = [b"data"]
        mock_get.return_value = mock_resp

        dest = tmp_path / "a" / "b" / "c" / "file.csv"
        download_file("http://example.com/file.csv", dest)

        assert dest.parent.is_dir()


# ---------------------------------------------------------------------------
# download_dataset (integration-level, fully mocked)
# ---------------------------------------------------------------------------

class TestDownloadDataset:
    VALID_URL = "https://data.gov.ua/dataset/ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb"

    @patch("data_load.data_set.download_file")
    @patch("data_load.data_set.get_resource_urls")
    def test_returns_paths_for_each_resource(self, mock_urls, mock_dl, tmp_path):
        mock_urls.return_value = [
            {"id": "r1", "name": "file1", "url": "http://x.com/f1.csv", "format": "csv"},
            {"id": "r2", "name": "file2", "url": "http://x.com/f2.csv", "format": "csv"},
        ]
        mock_dl.return_value = None

        result = download_dataset(self.VALID_URL, output_folder=str(tmp_path))
        assert len(result) == 2

    @patch("data_load.data_set.get_resource_urls")
    def test_returns_empty_list_when_no_resources(self, mock_urls, tmp_path):
        mock_urls.return_value = []
        result = download_dataset(self.VALID_URL, output_folder=str(tmp_path))
        assert result == []

    @patch("data_load.data_set.download_file")
    @patch("data_load.data_set.get_resource_urls")
    def test_continues_on_single_download_error(self, mock_urls, mock_dl, tmp_path):
        mock_urls.return_value = [
            {"id": "r1", "name": "ok", "url": "http://x.com/ok.csv", "format": "csv"},
            {"id": "r2", "name": "bad", "url": "http://x.com/bad.csv", "format": "csv"},
        ]
        mock_dl.side_effect = [None, Exception("network error")]

        result = download_dataset(self.VALID_URL, output_folder=str(tmp_path))
        assert len(result) == 1
