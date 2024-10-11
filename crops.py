import dataclasses

from bs4 import BeautifulSoup

from data_fetcher import DataFetcher


@dataclasses.dataclass(kw_only=True)
class Crop:
    name: str
    seed_name: str
    edible: bool
    multiple_rarities: bool
    used_in_recipe: bool
    purchase_sources: dict[str:int]
    sell_prices: list[int] | None
    energy_values_by_rarity: list[int] | None
    health_values_by_rarity: list[int] | None


def get_crops() -> list[Crop]:
    data_fetcher = DataFetcher("https://stardewvalleywiki.com/Crops")

    raw_data: BeautifulSoup = data_fetcher.raw_data

    # Find all tables on the page
    tables = raw_data.find_all('table', class_='wikitable')

    crops: list[Crop] = []

    for table in tables:

        crop_name = table.find_previous('h3').text.strip()

        # Find the rows in the table
        rows = table.find_all('tr')
        # Extract the header to get crop details
        headers = [header.text.strip() for header in rows[0].find_all('th')]
        if headers[0] != "Seeds":
            continue

        table_data = [row.text.strip().split("\n") for row in rows[1:]]
        clean_data = [[sub_data for sub_data in data if sub_data.replace("\t", "").replace("\n", "")] for data in
                      table_data if data]
        is_edible = not "Inedible" in clean_data[0]
        multiple_rarities = len(clean_data[0]) == 16 if is_edible else len(clean_data[0]) == 7
        usable = "used in" in [header.casefold() for header in headers]
        seed_name = clean_data[0][0]
        purchase_data = clean_data[0][1].strip().split(" ")
        purchase_sources = {purchase_data[i][:-1]: int(purchase_data[i + 1].split(">")[-1][:-1]) for i in
                            range(0, len(purchase_data), 2)}

        sell_prices = clean_data[0][2:6] if multiple_rarities else [clean_data[0][2]]
        sell_prices = [int(price.replace("g", "")) for price in sell_prices]
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

        crops.append(
            Crop(
                name=crop_name,
                seed_name=seed_name,
                edible=is_edible,
                multiple_rarities=multiple_rarities,
                used_in_recipe=usable,
                purchase_sources=purchase_sources,
                sell_prices=sell_prices,
                energy_values_by_rarity=energy_values,
                health_values_by_rarity=health_values,
            )
        )
        return crops


if __name__ == '__main__':
    crops = get_crops()
