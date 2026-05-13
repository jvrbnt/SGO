import sys
import os
from pathlib import Path


os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("SECRET_PEPPER", "test-secret-pepper")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
