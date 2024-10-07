import sys

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QHeaderView, QComboBox, QLineEdit, QSlider, QWidget
from qframelesswindow import FramelessWindow, StandardTitleBar

from appearance import set_app_font, apply_day_theme, ToggleSwitch, toggle_day_night, apply_cool_night_theme
from fertilizer import get_fertilizers, Fertilizer
from ui.main_window_widget_init import Ui_main_window_widget as Ui_main_window


class CustomTitleBar(StandardTitleBar):
    """ Custom title bar with modified buttons """

    def __init__(self, parent):
        super().__init__(parent)

        # customize the style of title bar items
        self.titleLabel.setStyleSheet("""
        
        """)
        self.minBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)


class MainWindow(FramelessWindow):  # Inherit from FramelessWindow
    def __init__(self):
        super().__init__()

        # Set custom title bar
        self.setTitleBar(CustomTitleBar(self))

        # Initialize UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        self.ui.big_layout.setContentsMargins(0, 21, 0, 0)

        # Set the window icon and title
        self.setWindowIcon(QIcon("path_to_icon/logo.png"))  # Use an actual path to your icon
        self.setWindowTitle("Stardew Valley Crop Planner")

        # Add toggle
        self.toggle_switch = ToggleSwitch()
        self.ui.toggle_layout.addWidget(self.toggle_switch)
        self.toggle_switch.clicked.connect(
            lambda: toggle_day_night(QApplication.instance(), self.toggle_switch.is_checked))
        self.toggle_switch.clicked.connect(
            lambda: self.update_header_buttons(self.toggle_switch.is_checked))

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
        self.ui.crop_table_view.setSelectionBehavior(QHeaderView.SelectRows)
        self.ui.crop_table_view.setSelectionMode(QHeaderView.NoSelection)
        self.headers = ["Image", "Name", "Description", "Cost", "Growth Rate"]
        self.model.setHorizontalHeaderLabels(self.headers)

        # Stretch the columns to fill the available width
        header = self.ui.crop_table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.fertilizers: list[Fertilizer] = get_fertilizers()

        # Populate Settings Panel
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
                image_item.setData(val, Qt.DecorationRole)
                image_item.setSizeHint(val.size())
                item = image_item
            else:
                item = QStandardItem(str(val))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            row_data.append(item)
        self.model.appendRow(row_data)

    def update_header_buttons(self, state: bool):
        buttons = [self.titleBar.minBtn, self.titleBar.maxBtn, self.titleBar.closeBtn]
        if state:
            for button in buttons:
                button.setNormalColor(Qt.white)
        else:
            for button in buttons:
                button.setNormalColor(Qt.black)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.ui.crop_table_view.resizeRowsToContents()

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

    def load_settings(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

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

    def showEvent(self, a0):
        super().showEvent(a0)
        self.ui.crop_table_view.resizeRowsToContents()

    def closeEvent(self, a0):
        self.save_all_settings()
        super().closeEvent(a0)


if __name__ == '__main__':
    app = QApplication([])
    set_app_font(app)
    window = MainWindow()
    toggle_day_night(app, window.toggle_switch.is_checked)
    window.update_header_buttons(window.toggle_switch.is_checked)
    window.show()
    sys.exit(app.exec())
