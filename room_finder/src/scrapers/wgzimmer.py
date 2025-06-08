import time
import random
import logging
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .. import config

BASE_URL = "https://www.wgzimmer.ch"
SEARCH_URL = "https://www.wgzimmer.ch/wgzimmer/search/mate.html"


def _parse_html(html_content: str, city_name: str) -> list[dict]:
    """
    Parses the raw HTML from Playwright to extract listing data.
    This is based on the proven logic from our proof-of-concept.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    results = soup.find_all("li", class_="search-result-entry", recursive=True)
    found_rooms = []

    for result in results:
        # Skip ad slots which sometimes use a similar class
        if "search-result-entry-slot" in result.get("class", []):
            continue

        # Ensure all necessary tags are present before processing
        id_val = result.get("id")
        link_tag = result.find("a", recursive=True)
        title_tag = result.find("h4")
        date_tag = result.find("span", class_="from-date")
        price_tag = result.find("span", class_="cost")

        if not all([id_val, link_tag, title_tag, date_tag, price_tag]):
            continue

        url = BASE_URL + link_tag["href"]
        title = title_tag.text.strip()
        date = date_tag.text.strip()
        price = price_tag.text.strip()

        # Return the data in the standardized dictionary format for the main script
        found_rooms.append(
            {
                "id": url,  # Use the unique URL as the ID
                "title": f"{title} [{city_name}]",
                "details": f"Price: {price} CHF | Available from: {date} | URL: {url}",
                "source": "WGZimmer",
            }
        )

    return found_rooms


def scrape_wgzimmer() -> list[dict]:
    """
    Scrapes wgzimmer.ch using Playwright to bypass anti-bot measures.
    It iterates through the cities defined in config.py.
    """
    logging.info("--- Starting WGZimmer.ch Playwright scrape ---")
    all_found_rooms = []

    # 1. Resolve city names from config into a final set of codes to search
    all_zurich_codes = [
        code for code in config.CITY_NAMES.values() if code.startswith("zurich")
    ]
    code_to_name_map = {v: k for k, v in config.CITY_NAMES.items()}
    final_city_codes_to_search = set()

    for city_name in config.CITIES_TO_SEARCH_BY_NAME:
        if city_name == "Zurich (ALL)":
            final_city_codes_to_search.update(all_zurich_codes)
        else:
            city_code = config.CITY_NAMES.get(city_name)
            if city_code:
                final_city_codes_to_search.add(city_code)
            else:
                logging.warning(
                    f"'{city_name}' from config is not a valid city name. Skipping."
                )

    if not final_city_codes_to_search:
        logging.warning("No valid cities configured for WGZimmer scrape.")
        return []

    # 2. Loop through each city and perform the scrape with Playwright
    with sync_playwright() as p:
        for city_code in final_city_codes_to_search:
            city_name = code_to_name_map.get(city_code, city_code)
            logging.info(f"-> WGZimmer: Searching in '{city_name}'...")

            ua = UserAgent().random
            browser = None
            try:
                browser = p.chromium.launch(
                    headless=config.HEADLESS_BROWSER, slow_mo=50
                )
                context = browser.new_context(user_agent=ua)
                page = context.new_page()

                page.goto(SEARCH_URL, timeout=60000, wait_until="domcontentloaded")

                # Handle the TCF consent button, which is the key step
                try:
                    page.locator(".fc-cta-consent").click(timeout=10000)
                    logging.info("Consent button clicked.")
                    page.wait_for_timeout(random.randint(1000, 2000))
                except Exception:
                    logging.info("Consent button not found or already handled.")

                # Fill form from values in config.py
                page.locator('select[name="priceMax"]').select_option(
                    config.WGZIMMER_SEARCH_CRITERIA_BASE["priceMax"]
                )
                page.locator('select[name="wgState"]').select_option(city_code)

                # Click the German "Search" button
                page.locator("input[value='Suchen']").click()

                # Use a fixed wait as requested, to allow the results (potentially in an iframe) to load
                logging.info("Waiting 10 seconds for results to load...")
                page.wait_for_timeout(10000)

                html_content = page.content()
                browser.close()

                # Parse the final HTML and add to our master list
                city_results = _parse_html(html_content, city_name)
                logging.info(f"Found {len(city_results)} listings in {city_name}.")
                all_found_rooms.extend(city_results)

            except Exception as e:
                logging.error(
                    f"[CRITICAL] Playwright failed for '{city_name}': {e}",
                    exc_info=True,
                )
                if browser:
                    browser.close()
                # Re-raise the exception so the main loop can catch it and send a notification
                raise e

    logging.info(
        f"--- WGZimmer scrape complete. Found a total of {len(all_found_rooms)} listings. ---"
    )
    return all_found_rooms
