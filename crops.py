from data_fetcher import DataFetcher
from bs4 import BeautifulSoup

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
        print("=============\n", crop_name, "\n", [[sub_data for sub_data in data if sub_data.replace("\t", "").replace("\n", "")] for data in table_data if data])
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) == len(headers):  # Check if the number of columns matches
                crop_data = {}
                for header, col in zip(headers, cols):
                    crop_data[header] = col.text.strip()  # Extract text and remove extra spaces
                crops.append(crop_data)

    return crops

if __name__ == '__main__':
    crops = get_crops()