import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDataWidgetMapper, QWidget, QApplication

from fertilizer import get_fertilizers
from ui.main_window_init import Ui_main_window


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # Table model
        self.model = QStandardItemModel()
        self.ui.crop_table_view.setModel(self.model)
        self.headers = ["Season", "Day", "Fertilizer"]
        self.model.setHorizontalHeaderLabels(self.headers)

        # Data Widget Mapper
        # self.mapper = QDataWidgetMapper()
        # self.mapper.setModel(self.model)
        # self.mapper.addMapping(self.ui.season_combo_box, 0)
        # self.mapper.addMapping(self.ui.day_spin_box, 1)
        # self.mapper.addMapping(self.ui.fertilizer_combo_box, 2)

        # Selection Model
        # selection_model = self.ui.crop_table_view.selectionModel()
        # selection_model.currentRowChanged.connect(self.mapper.setCurrentModelIndex)

        # Data Fetching
        self.ui.fertilizer_combo_box.addItems([obj.name for obj in get_fertilizers()])

        self.populate_table()

    def populate_table(self):
        for i in range(10):
            self.add_row([j * j for j in range(1, len(self.headers) + 1)])

    def add_row(self, data: list):
        row_data = [QStandardItem(str(val)) for val in data]
        self.model.appendRow(row_data)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
