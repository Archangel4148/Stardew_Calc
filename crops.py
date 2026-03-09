import dataclasses
import os

import requests
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from bs4 import BeautifulSoup

from data_fetcher import DataFetcher


@dataclasses.dataclass(kw_only=True)
class Crop:
    image_path: str
    image_name: str
    name: str
    seed_name: str
    edible: bool
    multiple_rarities: bool
    used_in_recipe: bool
    purchase_sources: dict[str, int]
    sell_prices: list[int] | None
    energy_values_by_rarity: list[int] | None
    health_values_by_rarity: list[int] | None
    growing_season: str
    growth_days: int
    regrowth_days: int | None


def get_crops() -> list[Crop]:
    data_fetcher = DataFetcher("https://stardewvalleywiki.com/Crops")

    raw_data: BeautifulSoup = data_fetcher.raw_data

    # Find all tables on the page
    tables = raw_data.find_all('table', class_='wikitable')

    crops: list[Crop] = []

    for table in tables:
        # Find the rows in the table
        rows = table.find_all('tr')

        # Extract the header to get crop details
        headers = [header.text.strip() for header in rows[0].find_all('th')]
        if headers[0] != "Seeds":
            continue

        crop_name = table.find_previous('h3').text.strip()
        crop_image_path = table.find_previous('img')['src']
        crop_image_name = crop_name.casefold().replace(" ", "_") + ".png"

        table_data = [row.text.strip().split("\n") for row in rows[1:]]
        clean_data = [[sub_data for sub_data in data if sub_data.replace("\t", "").replace("\n", "")] for data in
                      table_data if data]
        is_edible = "Inedible" not in clean_data[0]
        multiple_rarities = len(clean_data[0]) in (15, 16) if is_edible else len(clean_data[0]) in (7, 8)
        usable = "used in" in [header.casefold() for header in headers]
        seed_name = clean_data[0][0]

        purchase_data = clean_data[0][1].strip().split(" ")
        if len(purchase_data[0]) > 0:
            purchase_sources = {}
            shop_name = ""
            for item in purchase_data:
                if ":" in item:
                    shop_name += f" {item}"
                elif ">" in item:
                    purchase_sources[shop_name.strip().replace(":", "")] = int(
                        item.split(">")[-1][:-1].replace(",", ""))
                    shop_name = ""
                else:
                    shop_name += f" {item}"
        else:
            purchase_sources = {}

        if multiple_rarities:
            prices = clean_data[1:5]
        else:
            prices = [[clean_data[0][2]]]

        # Clean up sell prices
        sell_prices = [int(price[0].replace("g", "").replace(",", "").replace(" each", "").split(">")[-1]) for price in
                       prices]

        if is_edible:
            if usable:
                energy_values = list(map(int, clean_data[0][-9:-1:2]))
                health_values = list(map(int, clean_data[0][-8:-1:2]))
            else:
                energy_values = list(map(int, clean_data[0][-8:-1:2]))
                health_values = list(map(int, clean_data[0][-7:len(clean_data[0]):2]))
        else:
            energy_values = None
            health_values = None

        # Get growth time values
        growth_time_data = [d for d in clean_data[-1] if "Total" in d or "Regrowth" in d]
        growth_days = int(growth_time_data[0].split()[1])
        regrowth_days = None
        if len(growth_time_data) > 1:
            regrowth_days = int(growth_time_data[1].replace(":", " ").split()[1])

        # Get the most recent season
        season_header = table.find_previous('h2')
        season_text = season_header.text.strip() if season_header else None
        growing_season = season_text.replace(" Crops", "") if season_text else None

        crops.append(
            Crop(
                image_path=crop_image_path,
                image_name=crop_image_name,
                name=crop_name,
                seed_name=seed_name,
                edible=is_edible,
                multiple_rarities=multiple_rarities,
                used_in_recipe=usable,
                purchase_sources=purchase_sources,
                sell_prices=sell_prices,
                energy_values_by_rarity=energy_values,
                health_values_by_rarity=health_values,
                growing_season=growing_season,
                growth_days=growth_days,
                regrowth_days=regrowth_days,
            )
        )
    return crops


def check_and_download_images(crops: list[Crop], base_url: str):
    local_image_dir = 'local_images'  # Define your local image directory
    os.makedirs(local_image_dir, exist_ok=True)  # Create the directory if it doesn't exist

    for crop in crops:
        local_image_path = os.path.join(local_image_dir,
                                        crop.name.casefold().replace(" ", "_") + ".png")  # Adjust path as needed
        if not os.path.exists(local_image_path):
            download_image(base_url + crop.image_path, local_image_path)


def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(save_path, 'wb') as file:
            file.write(response.content)
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")


class CropFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.store_filter = "Any"
        self.season_filter = "Any"
        self.fertilizer_filter = "Normal Soil"
        self.day_filter = 1
        self.edible_filter = None
        self.regrow_filter = None
        self.regrow_day_filter = 1

    def filterAcceptsRow(self, row, parent):
        model = self.sourceModel()
        index = model.index(row, 0, parent)
        crop = model.data(index, Qt.UserRole + 1)

        if self.season_filter != "Any":
            if crop.growing_season != self.season_filter:
                return False

        if self.store_filter != "Any":
            if self.store_filter not in crop.purchase_sources.keys():
                return False

        if crop.growth_days > self.day_filter:
            return False

        if self.edible_filter is not None and crop.edible != self.edible_filter:
            return False

        if self.regrow_filter is not None and self.regrow_filter != (crop.regrowth_days is None):
            return False

        if self.regrow_filter and crop.regrowth_days > self.regrow_day_filter:
            return False

        return True


if __name__ == '__main__':
    crops = get_crops()
