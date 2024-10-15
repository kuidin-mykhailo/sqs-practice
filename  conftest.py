import sys

from pathlib import Path

here = Path("src").resolve().as_posix()
sys.path.insert(0, str(here))