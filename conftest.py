import sys
from pathlib import Path

# add src/ to path so tests can import source modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
