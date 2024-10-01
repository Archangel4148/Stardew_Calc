import dataclasses

import regex as re
from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QPixmap
from bs4 import BeautifulSoup

from data_fetcher import DataFetcher


def parse_fertilizer_id(fertilizer_id: str):
    return fertilizer_id.replace("_", " ").title()


def parse_cost_string(cost: str) -> float | None:
    # Example cost string: 100g (Spring 15, Year 1+)
    if cost.strip() in ("", "N/A"):
        return None
    else:
        # Regular expression to extract the cost values
        match = re.search(r'data-sort-value="(\d+)">(\d+)g', cost)
        if match:
            result = float(match.group(2))  # Convert the extracted cost to a float
            return result


def extract_growth_rate(description: str) -> float | None:
    if "growth rate" in description.casefold():
        match = re.search(r"(\d+)%", description)
        if match:
            return 1 + float(match.group(1)) / 100
    return 1.0


def parse_quality_fertilizer_values(soup: BeautifulSoup) -> dict[str:dict[str:dict[str:str]]]:
    """
    Extract data from fertilizer tables
    Args:
        soup: BeautifulSoup object

    Returns:
        Dictionary of fertilizer data, formatted as:
        {
            "soil_type": {
                "level": {
                    "Regular Quality": str, (percentage)
                    "Silver Quality": str, (percentage)
                    "Gold Quality": str, (percentage)
                    "Iridium Quality": str, (percentage)
                    "Average Price": str (factor modifier)
                }
            }
        }
    """
    crop_rarities = ["Regular Quality", "Silver Quality", "Gold Quality", "Iridium Quality"]
    # Rarities of crops available with each soil type
    soil_types: dict[str:list[bool]] = {
        "Normal_soil": [True, True, True, False],
        "Soil_with_Basic_Fertilizer": [True, True, True, False],
        "Soil_with_Quality_Fertilizer": [True, True, True, False],
        "Soil_with_Deluxe_Fertilizer": [False, True, True, True],
    }

    fertilizer_data: dict[str:dict] = {
        "Normal Soil": {str(i): {} for i in range(15)},
        "Basic Fertilizer": {str(i): {} for i in range(15)},
        "Quality Fertilizer": {str(i): {} for i in range(15)},
        "Deluxe Fertilizer": {str(i): {} for i in range(15)},
    }

    # Extract data from each soil table
    for soil_type in soil_types:
        table = soup.find('span', {'id': soil_type}).find_next('table')
        rows = table.find_all('tr')

        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')

            data_level = {
                'Regular Quality': None,
                'Silver Quality': None,
                'Gold Quality': None,
                'Iridium Quality': None,
                'Average Price': None
            }

            # Generate list of values that should be present
            present_values: list[str] = ["Farming Level"]
            for i, quality in enumerate(crop_rarities):
                if soil_types[soil_type][i]:
                    present_values.append(quality)
            present_values.append("Average Price")

            farming_level = cols[0].text.strip()
            for i in range(1, 5):
                data_level[present_values[i]] = cols[i].text.strip()

            fertilizer_data[parse_fertilizer_id(soil_type).replace("Soil With ", "")][farming_level] = data_level

    return fertilizer_data


def get_fertilizers():
    data_fetcher = DataFetcher("https://stardewvalleywiki.com/Fertilizer")
    table = data_fetcher.raw_data.find('span', {'id': 'Types_of_Fertilizer'}).find_next('table')
    rows = table.find_all('tr')

    # Extract data
    fertilizer_images: list[str] = [row.find_all('td')[0].find('img')['src'] for row in rows[1:]]
    fertilizer_names: list[str] = [row.find_all('td')[1].text.strip() for row in rows[1:]]
    fertilizer_descriptions: list[str] = [row.find_all('td')[2].text.strip() for row in rows[1:]]
    fertilizer_costs: list[float] = [parse_cost_string(row.find_all('td')[4].text) for row in rows[1:]]
    fertilizer_growth_rates: list[float] = [extract_growth_rate(description) for description in fertilizer_descriptions]

    # Account for regular soil
    print(fertilizer_images)
    fertilizer_images.insert(0, "/mediawiki/images/1/15/Gravel_Path.png")
    fertilizer_names.insert(0, "Normal Soil")
    fertilizer_descriptions.insert(0, "Does some soil stuff.")
    fertilizer_costs.insert(0, 0.0)
    fertilizer_growth_rates.insert(0, 1.0)

    fertilizer_pixmaps: list[QPixmap] = []
    for image_url in fertilizer_images:
        response = data_fetcher.get_image_data(image_url)
        # Convert the image data to QPixmap
        image_data = QByteArray(response)  # Convert to QByteArray
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)  # Load QPixmap from QByteArray
        fertilizer_pixmaps.append(pixmap)


    fertilizer_objects: list[Fertilizer] = []

    quality_fertilizer_data = parse_quality_fertilizer_values(data_fetcher.raw_data)

    # Create Fertilizer objects
    for i, name in enumerate(fertilizer_names):
        # Quality Fertilizer
        if name in quality_fertilizer_data:
            data = quality_fertilizer_data[name]
            value_rates_by_level = [data[farming_level]["Average Price"] for farming_level in data]
            silver_rates_by_level = [data[farming_level]["Silver Quality"] for farming_level in data]
            gold_rates_by_level = [data[farming_level]["Gold Quality"] for farming_level in data]
            iridium_rates_by_level = [data[farming_level]["Iridium Quality"] for farming_level in data]

            obj = Fertilizer(
                image=fertilizer_pixmaps[i],
                name=name.title(),
                category=" ".join(name.split()[1:]) if len(name) > 1 else name,
                description=fertilizer_descriptions[i],
                cost=fertilizer_costs[i],
                value_rates_by_farming_level=value_rates_by_level,
                silver_rate_by_farming_level=silver_rates_by_level,
                gold_rate_by_farming_level=gold_rates_by_level,
                iridium_rate_by_farming_level=iridium_rates_by_level,
                growth_rate=fertilizer_growth_rates[i]
            )
        # Other Fertilizer
        else:
            obj = Fertilizer(
                image=fertilizer_pixmaps[i],
                name=name,
                category=" ".join(name.split()[1:]) if len(name) > 1 else name,
                description=fertilizer_descriptions[i],
                cost=fertilizer_costs[i],
                # Other fertilizers don't affect value rates
                value_rates_by_farming_level=[1.0] * 15,
                silver_rate_by_farming_level=[1.0] * 15,
                gold_rate_by_farming_level=[1.0] * 15,
                iridium_rate_by_farming_level=[1.0] * 15,
                growth_rate=fertilizer_growth_rates[i]
            )

        fertilizer_objects.append(obj)

    return fertilizer_objects


@dataclasses.dataclass
class Fertilizer:
    image: QPixmap
    name: str
    category: str
    description: str
    cost: float | None
    value_rates_by_farming_level: list[float]
    silver_rate_by_farming_level: list[float]
    gold_rate_by_farming_level: list[float]
    iridium_rate_by_farming_level: list[float]
    growth_rate: float
