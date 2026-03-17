import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List
import chardet


def detect_encoding(file_path: str) -> str:
    """Визначає кодування файлу"""
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)
        result = chardet.detect(raw_data)
        return result['encoding']


def read_csv_flexible(file_path: str) -> pd.DataFrame:
    """
    Гнучке читання CSV файлів з різними роздільниками та форматами
    """
    # Спочатку визначаємо кодування
    encoding = detect_encoding(file_path)

    # Пробуємо різні роздільники
    delimiters = [',', ';', '\t', '|']

    for delimiter in delimiters:
        try:
            # Спробуємо прочитати з помилками
            df = pd.read_csv(file_path,
                             encoding=encoding,
                             delimiter=delimiter,
                             on_bad_lines='skip',  # Пропускаємо проблемні рядки
                             engine='python')  # Використовуємо Python engine для кращої обробки помилок

            if len(df.columns) > 1:  # Якщо знайшли більше однієї колонки
                print(f"  Знайдено роздільник: '{delimiter}'")
                return df

        except Exception as e:
            continue

    # Якщо не вдалося, спробуємо прочитати як текст та розібрати вручну
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()[:100]  # Читаємо перші 100 рядків

        # Спробуємо визначити найпоширеніший роздільник
        delimiter_counts = {}

        for line in lines[:10]:
            for delim in delimiters:
                count = line.count(delim)
                if count > 0:
                    delimiter_counts[delim] = delimiter_counts.get(delim, 0) + count

        if delimiter_counts:
            best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
            print(f"  Автоматично визначено роздільник: '{best_delimiter}'")

            # Читаємо з визначеним роздільником
            df = pd.read_csv(file_path,
                             encoding=encoding,
                             delimiter=best_delimiter,
                             on_bad_lines='skip',
                             engine='python')
            return df
    except:
        pass

    # Останній варіант - читаємо як один стовпець
    print(f"  Не вдалося визначити структуру, читаємо як один стовпець")
    return pd.read_csv(file_path,
                       encoding=encoding,
                       header=None,
                       names=['data'],
                       on_bad_lines='skip',
                       engine='python')


def get_figures_directory():
    """
    Повертає шлях до директорії для збереження графіків
    """
    # Отримуємо шлях до кореневої директорії проекту
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Піднімаємося на рівень вище з src/

    # Шлях до reports/figures/
    figures_dir = os.path.join(project_root, 'reports', 'figures')

    # Створюємо директорію, якщо вона не існує
    os.makedirs(figures_dir, exist_ok=True)

    return figures_dir


def visualize_data(file_paths: List[str]):
    """
    Функція для візуалізації даних з завантажених файлів.
    Підтримує CSV та Excel файли.
    """
    print("\n=== Візуалізація даних ===")

    successful_files = 0
    figures_dir = get_figures_directory()
    print(f"Графіки будуть збережені в: {figures_dir}")

    for file_path in file_paths:
        try:
            print(f"\nОбробка файлу: {os.path.basename(file_path)}")

            # Визначаємо тип файлу
            file_ext = os.path.splitext(file_path)[1].lower()

            # Завантажуємо дані
            if file_ext == '.csv':
                df = read_csv_flexible(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                print(f"  Формат файлу {file_ext} не підтримується для візуалізації")
                continue

            if df.empty:
                print("  Файл порожній")
                continue

            print(f"  Розмір даних: {df.shape}")
            print(f"  Колонки: {list(df.columns)}")

            # Базова статистика
            print(f"  Базова статистика:")
            print(df.describe())

            # Створюємо візуалізації
            create_visualizations(df, os.path.basename(file_path), figures_dir)
            successful_files += 1

        except Exception as e:
            print(f"  Помилка при обробці {os.path.basename(file_path)}: {e}")
            continue

    print(f"\n=== Успішно оброблено файлів: {successful_files} з {len(file_paths)} ===")
    print(f"Всі графіки збережено в: {figures_dir}")


def create_visualizations(df: pd.DataFrame, filename: str, figures_dir: str):
    """
    Створює різні типи візуалізацій для DataFrame
    """
    # Базове ім'я файлу без розширення
    base_name = os.path.splitext(filename)[0]

    # Спроба конвертувати колонки в числові, де це можливо
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass

    # Визначаємо числові колонки
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    if len(numeric_cols) == 0:
        print("  Немає числових даних для візуалізації")
        # Спробуємо візуалізувати категоріальні дані
        create_categorical_visualizations(df, base_name, figures_dir)
        return

    # 1. Гістограма для числових колонок
    if len(numeric_cols) > 0:
        n_cols = min(3, len(numeric_cols))
        fig, axes = plt.subplots(1, n_cols, figsize=(5 * n_cols, 4))
        if n_cols == 1:
            axes = [axes]

        for i, col in enumerate(numeric_cols[:3]):
            df[col].dropna().hist(bins=30, edgecolor='black', ax=axes[i])
            axes[i].set_title(f'Гістограма: {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Частота')

        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, f'{base_name}_histograms.png'))
        plt.close()

    # 2. Матриця кореляції (якщо є більше 1 числової колонки)
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        correlation = df[numeric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                    fmt='.2f', square=True)
        plt.title('Матриця кореляції')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, f'{base_name}_correlation.png'))
        plt.close()

    # 3. Box plot для числових колонок
    if len(numeric_cols) > 0:
        plt.figure(figsize=(12, 6))
        df[numeric_cols].boxplot()
        plt.title('Box plot числових колонок')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, f'{base_name}_boxplot.png'))
        plt.close()

    # 4. Pair plot для перших 5 числових колонок (якщо є)
    if 2 <= len(numeric_cols) <= 5:
        try:
            pair_plot = sns.pairplot(df[numeric_cols].dropna())
            pair_plot.savefig(os.path.join(figures_dir, f'{base_name}_pairplot.png'))
            plt.close()
        except:
            pass

    print(f"  Графіки збережено в {figures_dir}")


def create_categorical_visualizations(df: pd.DataFrame, base_name: str, figures_dir: str):
    """
    Створює візуалізації для категоріальних даних
    """
    # Знаходимо категоріальні колонки
    categorical_cols = df.select_dtypes(include=['object']).columns

    if len(categorical_cols) == 0:
        return

    # Стовпчикова діаграма для першої категоріальної колонки
    if len(categorical_cols) > 0:
        col = categorical_cols[0]
        plt.figure(figsize=(12, 6))

        # Отримуємо топ-20 категорій
        value_counts = df[col].value_counts().head(20)

        if len(value_counts) > 0:
            value_counts.plot(kind='bar')
            plt.title(f'Топ-20 значень: {col}')
            plt.xlabel(col)
            plt.ylabel('Частота')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, f'{base_name}_categorical.png'))
            plt.close()
            print(f"  Створено візуалізацію категоріальних даних")