import dataclasses

from bs4 import BeautifulSoup

from data_fetcher import scrape_url


def parse_fertilizer_id(fertilizer_id: str):
    return fertilizer_id.replace("_", " ").title()


def fertilizer_sort_key(fertilizer):
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


def parse_fertilizer_quality_tables(soup: BeautifulSoup) -> dict[str:dict]:
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
    raw_data = scrape_url("https://stardewvalleywiki.com/Fertilizer")
    fertilizers: list[Fertilizer] = []
    fertilizer_names: list[str] = []
    # Get fertilizers and add them to the list
    for row in raw_data.select("tr"):
        columns = row.find_all("td")
        if columns:
            for col in columns:
                text = col.get_text(strip=True).casefold()
                if "fertilizer" in text:
                    for fertilizer in text.split("•"):
                        if fertilizer not in fertilizer_names:
                            fertilizer_names.append(fertilizer)
    fertilizer_names = [f.title() for f in sorted(fertilizer_names, key=fertilizer_sort_key)]

    fertilizer_data = parse_fertilizer_quality_tables(raw_data)

    # Create Fertilizer objects
    for name in fertilizer_names:
        if name in fertilizer_data:
            data = fertilizer_data[name]
            category = name.split()[1:] if len(name) > 1 else name
            description = f"Does some fertilizer stuff."
            value_rates_by_level = [data[farming_level]["Average Price"] for farming_level in data]
            silver_rates_by_level = [data[farming_level]["Silver Quality"] for farming_level in data]
            gold_rates_by_level = [data[farming_level]["Gold Quality"] for farming_level in data]
            iridium_rates_by_level = [data[farming_level]["Iridium Quality"] for farming_level in data]
            growth_rate = 69

            obj = Fertilizer(
                name=name.title(),
                category=category,
                description=description,
                value_rates_by_farming_level=value_rates_by_level,
                silver_rate_by_farming_level=silver_rates_by_level,
                gold_rate_by_farming_level=gold_rates_by_level,
                iridium_rate_by_farming_level=iridium_rates_by_level,
                growth_rate=growth_rate
            )

        else:
            obj = Fertilizer(
                name=name.title(),
                category=name.split()[1:] if len(name) > 1 else name,
                description=f"Does some fertilizer stuff.",
                value_rates_by_farming_level=[],
                silver_rate_by_farming_level=[],
                gold_rate_by_farming_level=[],
                iridium_rate_by_farming_level=[],
                growth_rate=69
            )

        fertilizers.append(obj)

    return fertilizers


@dataclasses.dataclass
class Fertilizer:
    name: str
    category: str
    description: str
    value_rates_by_farming_level: list[float]
    silver_rate_by_farming_level: list[float]
    gold_rate_by_farming_level: list[float]
    iridium_rate_by_farming_level: list[float]
    growth_rate: float
