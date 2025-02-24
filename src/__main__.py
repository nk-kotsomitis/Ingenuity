import sys
from PySide6.QtWidgets import QApplication
from engine import EngineMain


def main():
    app = QApplication(sys.argv)
    window = EngineMain()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
