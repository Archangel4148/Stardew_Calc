import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QHeaderView

from appearance import set_app_font, apply_day_theme, ToggleSwitch, toggle_day_night, apply_cool_night_theme
from fertilizer import get_fertilizers, Fertilizer
from ui.main_window_init import Ui_main_window


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # Add toggle
        self.toggle_switch = ToggleSwitch()
        self.ui.toggle_layout.addWidget(self.toggle_switch)
        self.toggle_switch.clicked.connect(
            lambda: toggle_day_night(QApplication.instance(), self.toggle_switch.is_checked))

        # Table model
        self.model = QStandardItemModel()
        self.ui.crop_table_view.setModel(self.model)
        self.headers = ["Image", "Name", "Description", "Cost", "Growth Rate"]
        self.model.setHorizontalHeaderLabels(self.headers)

        # Stretch the columns to fill the available width
        header = self.ui.crop_table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Data Widget Mapper
        # self.mapper = QDataWidgetMapper()
        # self.mapper.setModel(self.model)
        # self.mapper.addMapping(self.ui.season_combo_box, 0)
        # self.mapper.addMapping(self.ui.day_spin_box, 1)
        # self.mapper.addMapping(self.ui.fertilizer_combo_box, 2)

        # Selection Model
        # selection_model = self.ui.crop_table_view.selectionModel()
        # selection_model.currentRowChanged.connect(self.mapper.setCurrentModelIndex)

        self.fertilizers: list[Fertilizer] = get_fertilizers()

        # Populating Settings Panel
        self.ui.fertilizer_combo_box.addItems([obj.name for obj in self.fertilizers])

        self.populate_table()

    def populate_table(self):
        for fertilizer in self.fertilizers:
            self.add_row(
                [
                    fertilizer.image,
                    fertilizer.name,
                    fertilizer.description,
                    fertilizer.cost,
                    fertilizer.growth_rate,
                ]
            )

    def add_row(self, data: list):
        row_data = []
        for val in data:
            if isinstance(val, QPixmap):
                # Create a QStandardItem for the image and set the pixmap
                image_item = QStandardItem()
                image_item.setData(val, Qt.DecorationRole)  # Use DecorationRole to store the pixmap
                image_item.setSizeHint(val.size())  # Set the size hint for the item to match the pixmap size
                row_data.append(image_item)
            else:
                # For other data types, convert to QStandardItem as usual
                row_data.append(QStandardItem(str(val)))
        self.model.appendRow(row_data)

    def resizeEvent(self, event):
        super().resizeEvent(event)  # Call the base class implementation
        self.ui.crop_table_view.resizeRowsToContents()  # Adjust row heights based on the new size


if __name__ == '__main__':
    app = QApplication([])
    set_app_font(app)
    window = MainWindow()
    toggle_day_night(app, window.toggle_switch.is_checked)
    window.show()
    sys.exit(app.exec())
