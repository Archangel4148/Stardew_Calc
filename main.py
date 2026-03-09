import json
import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSettings, QSortFilterProxyModel
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QHeaderView, QComboBox, QLineEdit, QSlider, QWidget, QLabel
from qframelesswindow import FramelessWindow, StandardTitleBar

from appearance import set_app_font, apply_day_theme, ToggleSwitch, toggle_day_night, apply_cool_night_theme
from crops import get_crops, Crop, check_and_download_images, CropFilterProxyModel
from fertilizer import get_fertilizers, Fertilizer
from ui.main_window_widget_init import Ui_main_window_widget as Ui_main_window


class CustomTitleBar(StandardTitleBar):
    """ Custom title bar with modified buttons """

    def __init__(self, parent):
        super().__init__(parent)
        # customize the style of title bar items
        self.titleLabel.setStyleSheet("""""")
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
    OFFLINE_MODE = False

    def __init__(self):
        super().__init__()

        # Set custom title bar
        self.setTitleBar(CustomTitleBar(self))

        # Initialize UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        self.ui.big_layout.setContentsMargins(0, 21, 0, 0)

        # Set the window icon and title
        self.setWindowTitle("Stardew Valley Crop Planner")

        # Add toggle
        self.toggle_switch = ToggleSwitch()
        self.ui.toggle_layout.addRow(QLabel("Day/Night"), self.toggle_switch)
        self.toggle_switch.clicked.connect(
            lambda: toggle_day_night(QApplication.instance(), self.toggle_switch.is_checked)
        )
        self.toggle_switch.clicked.connect(
            lambda: self.update_header_buttons(self.toggle_switch.is_checked)
        )

        # Load settings
        self.saved_fertilizer: str = ""
        self.saved_store: str = ""
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

        # Create a proxy model
        self.proxy_model = CropFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.ui.crop_table_view.setModel(self.proxy_model)
        self.ui.crop_table_view.setSelectionBehavior(QHeaderView.SelectRows)
        self.ui.crop_table_view.setSelectionMode(QHeaderView.NoSelection)
        self.headers = ["Crop Image", "Crop Name", "Seed Name", "Season", "Grow Time", "Edible",
                        "Purchase Sources", "Sell Price", "Energy Value", "Health Value"]
        self.model.setHorizontalHeaderLabels(self.headers)

        table = self.ui.crop_table_view
        header = table.horizontalHeader()

        # Prevent shrinking smaller than the header text
        for col in range(header.count()):
            min_width = header.sectionSizeHint(col)
            header.resizeSection(col, min_width)
            header.setMinimumSectionSize(min_width)

        # Allow columns to stretch to fill extra space
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Connect header click signal to sorting function
        header.sectionClicked.connect(self.handle_header_click)

        # Connect filter updates
        self.ui.store_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.season_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.fertilizer_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.day_spin_box.textChanged.connect(self.update_filters)

        if not self.OFFLINE_MODE:
            # Get data from wiki
            self.crops: list[Crop] = get_crops()
            self.fertilizers: list[Fertilizer] = get_fertilizers()

            # Check and download images
            check_and_download_images(self.crops, "https://stardewvalleywiki.com/")

            # Load from QSettings
            # Populate Settings Panel
            self.ui.fertilizer_combo_box.addItems([obj.name for obj in self.fertilizers])
            self.ui.fertilizer_combo_box.setCurrentText(self.saved_fertilizer)
            self.populate_table()
            self.ui.store_combo_box.setCurrentText(self.saved_store)
            self.update_filters()

        else:
            self.load_table_data()

    def handle_header_click(self, section):
        """Sort table based on header click."""
        # Toggle sort order between ascending and descending
        self.current_sort_order = (
            Qt.AscendingOrder if self.proxy_model.sortOrder() == Qt.DescendingOrder
            else Qt.DescendingOrder
        )
        self.proxy_model.sort(section, self.current_sort_order)

    def update_filters(self):
        self.proxy_model.store_filter = self.ui.store_combo_box.currentText()
        self.proxy_model.season_filter = self.ui.season_combo_box.currentText()
        self.proxy_model.fertilizer_filter = self.ui.fertilizer_combo_box.currentText()
        self.proxy_model.day_filter = self.ui.day_spin_box.value()

        self.proxy_model.invalidateFilter()

    def populate_table(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.headers)
        purchase_locations = []
        for i, crop in enumerate(self.crops):
            image_path = os.path.join("local_images", crop.image_name)
            growth_days_str = f"{crop.growth_days}"
            if crop.regrowth_days is not None:
                growth_days_str += f" (Regrows in {crop.regrowth_days})"
            for store in crop.purchase_sources:
                if store not in purchase_locations:
                    purchase_locations.append(store)
            self.add_row(
                [
                    QPixmap(image_path),
                    crop.name,
                    crop.seed_name,
                    crop.growing_season,
                    growth_days_str,
                    crop.edible,
                    crop.purchase_sources,
                    crop.sell_prices,
                    crop.energy_values_by_rarity,
                    crop.health_values_by_rarity
                ],
                image_path,
                crop
            )
        self.populate_purchase_locations(purchase_locations)

    def populate_purchase_locations(self, locations: list[str]):
        combo_box = self.ui.store_combo_box
        combo_box.clear()
        combo_box.addItem("Any")
        combo_box.addItems(sorted(locations))

    def add_row(self, data: list, local_path: str, crop: Crop):
        row_data = []
        for val in data:
            if isinstance(val, QPixmap):
                # Create a QStandardItem for the image and set the pixmap
                image_item = QStandardItem()
                image_item.setData(val, Qt.DecorationRole)
                image_item.setSizeHint(val.size())
                image_item.setTextAlignment(Qt.AlignCenter)
                item = image_item
                item.setData(local_path, Qt.UserRole)
            else:
                item = QStandardItem(str(val))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setData(crop, Qt.UserRole + 1)
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
                elif widget_name == "store_combo_box":
                    self.saved_store = self.settings.value(f"{widget_name}_text", "Any", type=str)
            elif isinstance(widget, QLineEdit):
                widget.setText(self.settings.value(f"{widget_name}_text", ""))
            elif isinstance(widget, ToggleSwitch):
                widget.is_checked = (self.settings.value(f"{widget_name}_checked", False, type=bool))
            elif isinstance(widget, QSlider):
                widget.setValue(self.settings.value(f"{widget_name}_value", 0, type=int))

    def save_table_data(self):
        # Prepare data for saving
        crops_data = []
        for row in range(self.model.rowCount()):
            row_data = []
            for column in range(self.model.columnCount()):
                item = self.model.item(row, column)
                if item:
                    if column == 0:  # For images, you might want to save a file path or identifier
                        row_data.append(item.data(Qt.UserRole))  # Placeholder, adjust accordingly
                    else:
                        row_data.append(item.text())
            crops_data.append(row_data)

        # Save to QSettings
        self.settings.setValue("crops_data", json.dumps(crops_data))

    def load_table_data(self):
        # Load from QSettings
        crops_data_json = self.settings.value("crops_data", "[]", type=str)
        crops_data = json.loads(crops_data_json)
        if crops_data:
            # Clear the current model and populate with loaded data
            self.model.clear()
            self.model.setHorizontalHeaderLabels(self.headers)
            crop_lookup = {crop.name: crop for crop in self.crops}
            for row_data in crops_data:
                image_path = row_data[0]
                row_data[0] = QPixmap(image_path)
                crop_name = row_data[1]
                crop_obj = crop_lookup.get(crop_name)
                self.add_row(row_data, local_path=image_path, crop=crop_obj)

    def showEvent(self, a0):
        super().showEvent(a0)
        self.ui.crop_table_view.resizeRowsToContents()

    def closeEvent(self, a0):
        self.save_all_settings()
        self.save_table_data()
        super().closeEvent(a0)


if __name__ == '__main__':
    app = QApplication([])
    set_app_font(app)
    window = MainWindow()
    toggle_day_night(app, window.toggle_switch.is_checked)
    window.update_header_buttons(window.toggle_switch.is_checked)
    window.show()
    sys.exit(app.exec())
