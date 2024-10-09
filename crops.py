from bs4 import BeautifulSoup

from data_fetcher import DataFetcher


def get_crops():
    data_fetcher = DataFetcher("https://stardewvalleywiki.com/Crops")

    raw_data: BeautifulSoup = data_fetcher.raw_data

    # Find all tables on the page
    tables = raw_data.find_all('table', class_='wikitable')

    crops = []

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
        purchase_source = clean_data[0][1]
        sell_prices = clean_data[0][2:6] if multiple_rarities else [clean_data[0][2]]
        if is_edible:
            # edible + rare = 16
            if usable:
                energy_values = clean_data[0][-9:-1:2]
                health_values = clean_data[0][-8:-1:2]
            else:
                energy_values = clean_data[0][-8:-1:2]
                health_values = clean_data[0][-7:len(clean_data[0]):2]
        else:
            # inedible + rare = 7
            energy_values = "None"
            health_values = "None"

        # print("========\n", crop_name, f"\nEdible: {is_edible}\n", clean_data)
        print(f"=============\n{crop_name}\nSeed: {seed_name}\nEdible: {is_edible}\nMultiple Rarities: {multiple_rarities}\nUsable: {usable}\nPurchase Source: {purchase_source}\nSell Prices: {sell_prices}\nEnergy Values: {energy_values}\nHealth Values: {health_values}")


if __name__ == '__main__':
    crops = get_crops()
