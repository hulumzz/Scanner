import sys
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
# Unit tests use isolated databases and must never depend on a developer's .env.
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
