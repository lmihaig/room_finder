import requests
from bs4 import BeautifulSoup
import bs4
from .. import config
import logging


def _extract_data_from_single_item(item: bs4.element.Tag):
    """Helper function to parse a single WOKO listing item."""
    try:
        table_entries = item.find("table").findChildren("td")
        title = table_entries[0].text.strip()
        date = table_entries[1].text.strip()
        address = table_entries[3].text.strip()
        price = item.find("div", attrs={"class": "preis"}).text.strip()
        return title, date, address, price
    except (AttributeError, IndexError) as e:
        print(f"Could not parse a WOKO item: {e}")
        return None


def scrape_woko():
    """Scrapes the WOKO website for room listings."""
    print("Scraping WOKO...")
    try:
        raw_html = requests.get(config.WOKO_URL, timeout=10).content.decode()
        html = BeautifulSoup(raw_html, features="lxml")
        lettings_list = html.body.find_all("div", attrs={"class": "inserat"})

        all_rooms = []
        for item in lettings_list:
            data = _extract_data_from_single_item(item)
            if data:
                title, date, address, price = data
                all_rooms.append(
                    {
                        "id": data,
                        "title": f"{title} ({date})",
                        "details": f"Price: {price}, Address: {address}",
                        "source": "WOKO",
                    }
                )
        logging.info(f"Found {len(all_rooms)} listings on WOKO.")
        return all_rooms
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching WOKO page: {e}")
        return []
