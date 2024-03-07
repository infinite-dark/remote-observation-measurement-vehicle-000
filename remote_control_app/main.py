import sys
from PySide6.QtWidgets import QApplication
from rcmp.widgets import RCMPApp


def main():
    if len(sys.argv) > 1:
        addr = str(sys.argv[1])
    else:
        addr = "10.0.0.1"

    app = QApplication(sys.argv)
    window = RCMPApp(addr)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
