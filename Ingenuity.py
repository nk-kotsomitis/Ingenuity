# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

try:
    import pyi_splash
    # Update the text on the splash screen
    pyi_splash.update_text("PyInstaller is a great software!")
    pyi_splash.update_text("Second time's a charm!")
    # Close the splash screen
    pyi_splash.close()
except ImportError:
    # pyi_splash is only available in a PyInstaller-built app
    pass

from src.__main__ import main
main()
