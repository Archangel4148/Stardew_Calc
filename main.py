import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from ui.main_window_init import Ui_main_window
from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # Table model
        self.model = QStandardItemModel()
        self.ui.crop_table_view.setModel(self.model)

        self.populate_table()

    def populate_table(self):
        row_count, column_count = 10, 3

        self.model.setHorizontalHeaderLabels([f"Header {i+1}" for i in range(column_count)])

        for i in range(row_count):
            self.add_row([j * j for j in range(column_count)])

    def add_row(self, data: list):
        row_data = [QStandardItem(str(val)) for val in data]
        self.model.appendRow(row_data)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
