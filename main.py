import sys

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QHeaderView, QComboBox, QLineEdit, QSlider, QMainWindow

from appearance import set_app_font, apply_day_theme, ToggleSwitch, toggle_day_night, apply_cool_night_theme
from fertilizer import get_fertilizers, Fertilizer
from ui.main_window_init import Ui_main_window


class MainWindow(QMainWindow):
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

        # Load settings
        self.saved_fertilizer: str = ""
        self.settings = QSettings("MyCompany", "StardewCalc")
        self.load_settings()

        # Apply saved theme
        if self.settings.value("theme", "day") == "night":
            self.toggle_switch.setChecked(True)
            apply_cool_night_theme(QApplication.instance())
        else:
            self.toggle_switch.setChecked(False)
            apply_day_theme(QApplication.instance())

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
        self.ui.fertilizer_combo_box.setCurrentText(self.saved_fertilizer)

        self.populate_table()

    def populate_table(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.headers)
        for fertilizer in self.fertilizers:
            self.add_row(
                [
                    fertilizer.image,
                    fertilizer.name,
                    fertilizer.description,
                    str(fertilizer.cost).replace(".0", "gp"),
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

    def save_all_settings(self):
        # Save toggle state and theme preference
        self.settings.setValue("theme", "night" if self.toggle_switch.is_checked else "day")

        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())

        # Automatically save all widget states
        for widget in self.findChildren(QWidget):
            widget_name = widget.objectName()
            if isinstance(widget, QComboBox):
                self.settings.setValue(f"{widget_name}_text", widget.currentText())
            elif isinstance(widget, QLineEdit):
                self.settings.setValue(f"{widget_name}_text", widget.text())
            elif isinstance(widget, ToggleSwitch):
                self.settings.setValue(f"{widget_name}_checked", widget.is_checked)
            elif isinstance(widget, QSlider):
                self.settings.setValue(f"{widget_name}_value", widget.value())
            # Add more widget types as needed

    def load_settings(self):
        # Restore window geometry and other saved settings
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Automatically load all widget states
        for widget in self.findChildren(QWidget):
            widget_name = widget.objectName()
            if isinstance(widget, QComboBox):
                widget.setCurrentText(self.settings.value(f"{widget_name}_text", "Normal Soil", type=str))
                if widget_name == "fertilizer_combo_box":
                    self.saved_fertilizer = self.settings.value(f"{widget_name}_text", "Normal Soil", type=str)
            elif isinstance(widget, QLineEdit):
                widget.setText(self.settings.value(f"{widget_name}_text", ""))
            elif isinstance(widget, ToggleSwitch):
                widget.is_checked = (self.settings.value(f"{widget_name}_checked", False, type=bool))
            elif isinstance(widget, QSlider):
                widget.setValue(self.settings.value(f"{widget_name}_value", 0, type=int))
            # Add more widget types as needed

    def closeEvent(self, event):
        # Save all widget states and settings on close
        self.save_all_settings()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    set_app_font(app)
    window = MainWindow()
    toggle_day_night(app, window.toggle_switch.is_checked)
    window.show()
    sys.exit(app.exec())
