"""Пайплайн візуалізації: будує графіки з CSV на спільному томі."""

from __future__ import annotations

import sys
from pathlib import Path

from constants import DOWNLOADS_FOLDER
from visualization.visualize import visualize_data


def main() -> int:
    root = Path(DOWNLOADS_FOLDER)
    paths = [str(p) for p in sorted(root.rglob("*.csv"))] if root.exists() else []
    if not paths:
        print("CSV не знайдені в", root)
        return 1
    visualize_data(paths)
    return 0


if __name__ == "__main__":
    sys.exit(main())
