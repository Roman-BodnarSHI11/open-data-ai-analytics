from constants import DATASETS_URLS
from data_set import download_dataset
from visualize import visualize_data


def main():
    print("=== Завантаження датасетів ===")
    all_files = []

    for url in DATASETS_URLS:
        print(f"\nОбробка: {url}")
        files = download_dataset(url)
        all_files.extend(files)

    print(f"\n=== Завершено. Завантажено файлів: {len(all_files)} ===")
    for f in all_files:
        print(f"  {f}")

    # Запуск візуалізації для завантажених файлів
    if all_files:
        visualize_data(all_files)


if __name__ == "__main__":
    main()