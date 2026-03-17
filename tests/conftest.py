"""Shared pytest fixtures and path configuration."""

import sys
from pathlib import Path

# Make src/ importable from any test module.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
