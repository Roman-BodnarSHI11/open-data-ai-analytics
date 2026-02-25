import os
import re
import requests
from pathlib import Path

from constants import CKAN_API_URL, DOWNLOADS_FOLDER


def extract_dataset_id(url: str) -> str:
    """Витягує UUID датасету з URL порталу data.gov.ua."""
    match = re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        url,
    )
    if not match:
        raise ValueError(f"Не вдалося знайти ID датасету в URL: {url}")
    return match.group(0)


def get_resource_urls(dataset_id: str) -> list[dict]:
    """Повертає список ресурсів датасету через CKAN API."""
    api_url = f"{CKAN_API_URL}/package_show"
    response = requests.get(api_url, params={"id": dataset_id}, timeout=30)
    response.raise_for_status()

    data = response.json()
    if not data.get("success"):
        raise RuntimeError(f"CKAN API повернув помилку для датасету {dataset_id}")

    resources = data["result"].get("resources", [])
    return [
        {
            "id": r["id"],
            "name": r.get("name", r["id"]),
            "url": r["url"],
            "format": r.get("format", "").lower(),
        }
        for r in resources
        if r.get("url")
    ]


def download_file(url: str, dest_path: Path) -> None:
    """Завантажує файл за URL і зберігає за вказаним шляхом."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Завантаження: {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"  Збережено: {dest_path}")


def download_dataset(dataset_url: str, output_folder: str = DOWNLOADS_FOLDER) -> list[Path]:
    """
    Завантажує всі ресурси датасету за URL сторінки на data.gov.ua.

    Повертає список шляхів до завантажених файлів.
    """
    dataset_id = extract_dataset_id(dataset_url)
    print(f"\nДатасет ID: {dataset_id}")

    resources = get_resource_urls(dataset_id)
    if not resources:
        print("  Ресурси не знайдені.")
        return []

    print(f"  Знайдено ресурсів: {len(resources)}")
    downloaded = []

    for res in resources:
        # Формуємо безпечне ім'я файлу
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", res["name"])
        ext = f".{res['format']}" if res["format"] and not safe_name.endswith(f".{res['format']}") else ""
        filename = f"{safe_name}{ext}"
        dest = Path(output_folder) / dataset_id / filename

        try:
            download_file(res["url"], dest)
            downloaded.append(dest)
        except Exception as e:
            print(f"  Помилка при завантаженні {res['url']}: {e}")

    return downloaded