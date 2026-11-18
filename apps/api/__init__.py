"""Paquete principal del backend FastAPI de Torre Satori PMS."""

from pathlib import Path
import sys

_API_DIR = str(Path(__file__).resolve().parent)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)
