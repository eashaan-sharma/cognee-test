"""Project paths and settings.

Cognee reads its own LLM and embedding settings straight from .env,
so this file only holds what our own scripts need.
"""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# cognee-test/ (one level above backend/)
ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"        # downloaded Wikipedia articles, one .txt each
COGNEE_DIR = DATA_DIR / "cognee"  # where Cognee keeps its graph + vector databases

RAW_DIR.mkdir(parents=True, exist_ok=True)
COGNEE_DIR.mkdir(parents=True, exist_ok=True)
