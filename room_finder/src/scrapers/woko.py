# src/scrapers/woko.py
import requests
from bs4 import BeautifulSoup, Tag
from .. import config
import logging

WOKO_BASE_URL = "https://www.woko.ch"


def _extract_data_from_single_item(item: Tag):
    """Helper function to parse a single WOKO listing item."""
    try:
        link_tag = item.find("a", href=True)
        if not link_tag:
            return None

        full_link = f"{WOKO_BASE_URL}{link_tag['href']}"

        table_entries = item.find("table").find_all("td")
        title = table_entries[0].text.strip()
        date = table_entries[1].text.strip()
        address = table_entries[3].text.strip()
        price = item.find("div", attrs={"class": "preis"}).text.strip()

        # Use the config flag that we restored
        if config.IGNORE_SUBLET and "sublet" in title.lower():
            logging.info(f"Ignoring WOKO sublet based on title: {title}")
            return None

        return {
            "id": full_link,
            "title": f"{title} ({date})",
            "details": f"Price: {price}, Address: {address}\nLink: {full_link}",
            "source": "WOKO",
        }
    except (AttributeError, IndexError) as e:
        logging.warning(
            f"Could not parse a WOKO item. It might be structured differently. Error: {e}"
        )
        return None


def scrape_woko():
    """Scrapes the WOKO website for room listings."""
    logging.info("Scraping WOKO...")
    try:
        raw_html = requests.get(config.WOKO_URL, timeout=10).content.decode()
        html = BeautifulSoup(raw_html, "lxml")
        lettings_list = html.body.find_all("div", attrs={"class": "inserat"})

        all_rooms = []
        for item in lettings_list:
            data = _extract_data_from_single_item(item)
            if data:
                all_rooms.append(data)

        logging.info(f"Found {len(all_rooms)} listings on WOKO.")
        return all_rooms
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching WOKO page: {e}")
        return []
