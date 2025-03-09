# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.__main__ import main
main()
