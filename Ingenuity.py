import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.__main__ import main
main()
