import sys

from ui.main_window_init import Ui_main_window
from PyQt5 import QtWidgets

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())