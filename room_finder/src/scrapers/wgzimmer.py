# src/scrapers/wgzimmer.py
# Corrected version that integrates the successful logic from the PoC.

import time
import random
import logging
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import stealth_sync  # <--- 1. Re-added stealth, a good practice
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List
from .. import config

BASE_URL = "https://www.wgzimmer.ch"
SEARCH_URL = "https://www.wgzimmer.ch/wgzimmer/search/mate.html"


def _parse_html(html_content: str, city_name: str) -> List[dict]:
    """
    Parses the raw HTML from Playwright to extract listing data.
    This function is unchanged as its logic was already correct.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    results = soup.find_all("li", class_="search-result-entry", recursive=True)
    found_rooms = []

    for result in results:
        if "search-result-entry-slot" in result.get("class", []):
            continue

        link_tag = result.find("a", href=True)
        if not link_tag:
            continue

        url = BASE_URL + link_tag.get("href", "")
        location_tag = link_tag.find("span", class_="thumbState")
        price_tag = link_tag.find("span", class_="cost")
        date_tag = link_tag.find("span", class_="from-date")
        posted_tag = result.find("div", class_="create-date")

        if all([location_tag, price_tag, date_tag]):
            location = (
                location_tag.find("strong").text.strip()
                if location_tag.find("strong")
                else "N/A"
            )
            price = price_tag.text.strip()
            date = date_tag.text.strip()
            posted = posted_tag.text.strip() if posted_tag else "N/A"
            title = f"{location}"

            found_rooms.append(
                {
                    "id": url,
                    "title": f"{title} [{city_name}]",
                    "details": f"Price: {price} | Available: {date} | Posted: {posted} | URL: {url}",
                    "source": "WGZimmer",
                }
            )

    return found_rooms


def scrape_wgzimmer() -> List[dict]:
    """
    Scrapes wgzimmer.ch using Playwright, strictly following the logic
    from the successful proof-of-concept script.
    """
    logging.info("--- Starting WGZimmer.ch Playwright scrape ---")
    all_found_rooms = []

    # --- City code logic remains the same ---
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

    with sync_playwright() as p:
        for city_code in final_city_codes_to_search:
            city_name = code_to_name_map.get(city_code, city_code)
            logging.info(f"-> WGZimmer: Searching in: {city_name}...")

            ua = UserAgent().random
            browser = None
            try:
                browser = p.chromium.launch(
                    headless=config.HEADLESS_BROWSER, slow_mo=250
                )
                context = browser.new_context(user_agent=ua)
                page = context.new_page()
                stealth_sync(page)  # <--- 2. Apply stealth to the page

                page.goto(SEARCH_URL, timeout=60000, wait_until="domcontentloaded")

                try:
                    consent_button = page.locator(".fc-cta-consent")
                    consent_button.wait_for(state="visible", timeout=10000)
                    logging.info("Consent button found. Clicking it...")
                    consent_button.click()
                except TimeoutError:
                    logging.info("Consent button not found or already handled.")

                logging.info("Filling search form...")
                page.locator('select[name="priceMax"]').select_option(
                    config.WGZIMMER_SEARCH_CRITERIA_BASE["priceMax"]
                )
                page.locator('select[name="wgState"]').select_option(city_code)
                time.sleep(1)  # Short pause like in PoC

                # --- 3. KEY CHANGE: Reverting to the PoC's successful submission and waiting logic ---
                logging.info("Submitting search and waiting for navigation...")
                with page.expect_navigation(
                    wait_until="domcontentloaded", timeout=60000
                ):
                    # Use 'press("Enter")' as it was proven to work reliably in the PoC
                    page.locator('input[name="query"]').press("Enter")

                logging.info(f"Navigation successful. URL is now: {page.url}")
                logging.info("Waiting for a REAL search result to load...")

                # Wait for a result that is NOT an ad, which confirms the page is ready.
                # This is the most critical part from the PoC.
                page.wait_for_selector(
                    "li.search-result-entry:not(.search-result-entry-slot)",
                    state="visible",
                    timeout=20000,
                )
                logging.info("Real result found. Capturing page content...")
                # --- END OF KEY CHANGE ---

                # A small, final delay to ensure all elements have settled.
                time.sleep(1)

                html_content = page.content()
                city_results = _parse_html(html_content, city_name)

                if not city_results:
                    # Your excellent debugging logic for when no results are found
                    debug_filename_base = f"debug_page_{city_code}"
                    screenshot_path = f"{debug_filename_base}.png"
                    html_path = f"{debug_filename_base}.html"
                    logging.warning(
                        f"Found 0 listings in {city_name}. Saving debug files."
                    )
                    page.screenshot(path=screenshot_path)
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    logging.warning(f"Screenshot saved to: {screenshot_path}")
                    logging.warning(f"HTML content saved to: {html_path}")

                logging.info(f"Found {len(city_results)} listings in {city_name}.")
                all_found_rooms.extend(city_results)

            except Exception as e:
                logging.error(
                    f"[CRITICAL] Playwright failed for {city_name}: {e}", exc_info=True
                )
                # No need to re-raise 'e', just let the loop continue if possible
            finally:
                if browser:
                    browser.close()

    logging.info(
        f"--- WGZimmer scrape complete. Found a total of {len(all_found_rooms)} listings. ---"
    )
    return all_found_rooms
