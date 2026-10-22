"""Chemins indépendants du répertoire de lancement."""
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RUNTIME_DIR = Path(os.environ.get("PERINATAL_RUNTIME_DIR", str(BASE_DIR / "data" / "private"))).expanduser().resolve()
ANALYSIS_DB = BASE_DIR / "data" / "perinatalite.db"
