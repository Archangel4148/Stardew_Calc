import requests
from bs4 import BeautifulSoup


class DataFetcher:
    def __init__(self, url: str):
        self.url = url
        self.raw_data = self.scrape_url()

    def scrape_url(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def get_image_data(self, image_reference: str):
        full_image_url = "https://stardewvalleywiki.com/" + image_reference
        image_content = requests.get(full_image_url).content
        return image_content
