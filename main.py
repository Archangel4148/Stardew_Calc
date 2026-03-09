import json
import os
from pathlib import Path
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSettings, QSortFilterProxyModel
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QHeaderView, QComboBox, QLineEdit, QSlider, QSpinBox, QWidget, QLabel
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
    OFFLINE_MODE = True
    DATA_DIR = Path("local_data")
    CROP_CACHE = DATA_DIR /"crop_cache.json"
    FERTILIZER_CACHE = DATA_DIR /"fertilizer_cache.json"

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

        # Connect regrow day spin box visibility updates
        self.toggle_regrow_day_visibility(self.ui.regrow_combo_box.currentText())
        self.ui.regrow_combo_box.currentTextChanged.connect(self.toggle_regrow_day_visibility)

        # Connect filter updates
        self.ui.store_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.season_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.fertilizer_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.day_spin_box.valueChanged.connect(self.update_filters)
        self.ui.edible_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.regrow_combo_box.currentTextChanged.connect(self.update_filters)
        self.ui.regrow_day_spin_box.valueChanged.connect(self.update_filters)

        if not self.OFFLINE_MODE:
            # Get data from wiki
            self.crops: list[Crop] = get_crops()
            self.fertilizers: list[Fertilizer] = get_fertilizers()

            # Cache data objects for offline use
            os.makedirs(self.DATA_DIR, exist_ok=True)
            with open(self.CROP_CACHE, "w") as f:
                json.dump([c.to_dict() for c in self.crops], f, indent=2)
            with open(self.FERTILIZER_CACHE, "w") as f:
                json.dump([c.to_dict() for c in self.fertilizers], f, indent=2)

            # Check and download images
            check_and_download_images(self.crops, "https://stardewvalleywiki.com/")
        else:
            # Load cached crop data
            with open(self.CROP_CACHE) as f:
                crop_data = json.load(f)
            self.crops = [Crop.from_dict(c) for c in crop_data]

            # Load fertilizer data
            with open(self.FERTILIZER_CACHE) as f:
                fertilizer_data = json.load(f)
            self.fertilizers = [Fertilizer.from_dict(c) for c in fertilizer_data]

        # Populate Settings Panel
        self.ui.fertilizer_combo_box.addItems([obj.name for obj in self.fertilizers])
        self.ui.fertilizer_combo_box.setCurrentText(self.saved_fertilizer)
        self.populate_table()
        self.ui.store_combo_box.setCurrentText(self.saved_store)
        self.update_filters()

    def handle_header_click(self, section):
        """Sort table based on header click."""
        # Toggle sort order between ascending and descending
        order = self.proxy_model.sortOrder()
        self.proxy_model.sort(section, Qt.DescendingOrder if order == Qt.AscendingOrder else Qt.AscendingOrder)

    def update_filters(self):
        self.proxy_model.store_filter = self.ui.store_combo_box.currentText()
        self.proxy_model.season_filter = self.ui.season_combo_box.currentText()
        self.proxy_model.fertilizer_filter = self.ui.fertilizer_combo_box.currentText()
        self.proxy_model.day_filter = self.ui.day_spin_box.value()

        edible_text = self.ui.edible_combo_box.currentText()
        if edible_text == "Any":
            self.proxy_model.edible_filter = None
        else:
            self.proxy_model.edible_filter = edible_text == "Yes"

        regrow_text = self.ui.regrow_combo_box.currentText()
        if regrow_text == "Any":
            self.proxy_model.regrow_filter = None
        else:
            self.proxy_model.regrow_filter = regrow_text == "Yes"

        self.proxy_model.regrow_day_filter = self.ui.regrow_day_spin_box.value()

        self.proxy_model.invalidateFilter()

    def populate_table(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.headers)
        purchase_locations = set()

        for crop in self.crops:
            image_path = os.path.join("local_images", crop.image_name)
            growth_days_str = f"{crop.growth_days}"
            if crop.regrowth_days is not None:
                growth_days_str += f" (Regrows in {crop.regrowth_days})"
            purchase_locations.update(crop.purchase_sources)
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

        self.ui.crop_table_view.resizeRowsToContents()

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

    def toggle_regrow_day_visibility(self, text: str):
        regrow = text == "Yes"
        self.ui.regrow_day_spin_box.setVisible(regrow)
        self.ui.regrow_day_label.setVisible(regrow)

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
            elif isinstance(widget, QSlider) or isinstance(widget, QSpinBox):
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
            elif isinstance(widget, QSlider) or isinstance(widget, QSpinBox):
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
