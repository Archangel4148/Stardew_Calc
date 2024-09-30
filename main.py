import sys

import requests
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDataWidgetMapper, QWidget, QApplication
from bs4 import BeautifulSoup

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
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.ui.season_combo_box, 0)
        self.mapper.addMapping(self.ui.day_spin_box, 1)
        self.mapper.addMapping(self.ui.fertilizer_combo_box, 2)

        # Selection Model
        selection_model = self.ui.crop_table_view.selectionModel()
        selection_model.currentRowChanged.connect(self.mapper.setCurrentModelIndex)

        # Data Fetcher
        self.fetcher = DataFetcher()
        self.ui.fertilizer_combo_box.addItems(self.fetcher.get_fertilizers())

        self.populate_table()

    def populate_table(self):
        for i in range(10):
            self.add_row([j * j for j in range(1, len(self.headers) + 1)])

    def add_row(self, data: list):
        row_data = [QStandardItem(str(val)) for val in data]
        self.model.appendRow(row_data)


class DataFetcher:
    def scrape_url(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def fertilizer_sort_key(self, fertilizer):
        categories = {
            "fertilizer": 1,
            "retaining": 5,
            "speed-gro": 10,
        }
        levels = {
            "no_quality": 1,
            "basic": 1,
            "quality": 2,
            "deluxe": 3,
            "hyper": 4,
        }
        parts = fertilizer.split()

        fertilizer_quality = parts[0] if len(parts) > 1 else "no_quality"
        fertilizer_type = parts[1] if len(parts) > 1 else parts[0]

        score = categories.get(fertilizer_type, 99) + levels.get(fertilizer_quality, 99)

        return score

    def get_fertilizers(self):
        raw_data = self.scrape_url("https://stardewvalleywiki.com/Fertilizer")
        fertilizers = []
        for row in raw_data.select("tr"):
            columns = row.find_all("td")
            if columns:
                for col in columns:
                    text = col.get_text(strip=True).casefold()
                    if "fertilizer" in text:
                        for fertilizer in text.split("•"):
                            if fertilizer not in fertilizers:
                                fertilizers.append(fertilizer)
        return [f.title() for f in sorted(fertilizers, key=self.fertilizer_sort_key)]

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
