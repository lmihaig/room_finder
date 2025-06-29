# src/scrapers/wgzimmer.py
import time
import logging
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List
from .. import config


def _parse_html(html_content: str, city_name: str) -> List[dict]:
    """Parses the raw HTML to extract listing data."""
    soup = BeautifulSoup(html_content, "html.parser")
    results = soup.find_all("li", class_="search-result-entry", recursive=True)
    found_rooms = []

    for result in results:
        if "search-result-entry-slot" in result.get("class", []):
            continue

        link_tag = result.find("a", href=True)
        if not link_tag:
            continue

        url = config.WGZIMMER_BASE_URL + link_tag.get("href", "")
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
                    "details": f"Price: {price} | Available: {date} | Posted: {posted}\nLink: {url}",
                    "source": "WGZimmer",
                }
            )
    return found_rooms


def scrape_wgzimmer() -> List[dict]:
    """Scrapes wgzimmer.ch using the robust logic from the original script."""
    logging.info("--- Starting WGZimmer.ch Playwright scrape ---")
    all_found_rooms = []

    # This logic is from your original script
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

    if not final_city_codes_to_search:
        logging.warning("No valid cities configured for WGZimmer scrape.")
        return []

    with sync_playwright() as p:
        for city_code in final_city_codes_to_search:
            city_name = code_to_name_map.get(city_code, city_code)
            logging.info(f"-> WGZimmer: Searching in: {city_name}...")
            browser = None
            try:
                browser = p.chromium.launch(
                    headless=config.HEADLESS_BROWSER, slow_mo=250
                )
                context = browser.new_context(user_agent=UserAgent().random)
                page = context.new_page()
                stealth_sync(page)

                page.goto(
                    config.WGZIMMER_SEARCH_URL,
                    timeout=60000,
                    wait_until="domcontentloaded",
                )

                try:
                    page.locator(".fc-cta-consent").wait_for(
                        state="visible", timeout=5000
                    )
                    page.locator(".fc-cta-consent").click()
                except TimeoutError:
                    logging.info("Consent button not found or already handled.")

                page.locator('select[name="priceMax"]').select_option(
                    config.WGZIMMER_SEARCH_CRITERIA_BASE["priceMax"]
                )
                page.locator('select[name="wgState"]').select_option(city_code)
                time.sleep(1)

                with page.expect_navigation(
                    wait_until="domcontentloaded", timeout=60000
                ):
                    page.locator('input[name="query"]').press("Enter")

                page.wait_for_selector(
                    "li.search-result-entry:not(.search-result-entry-slot)",
                    state="visible",
                    timeout=20000,
                )
                time.sleep(1)

                html_content = page.content()
                city_results = _parse_html(html_content, city_name)
                all_found_rooms.extend(city_results)

            except Exception as e:
                logging.error(
                    f"[CRITICAL] Playwright failed for {city_name}: {e}", exc_info=True
                )
            finally:
                if browser:
                    browser.close()

    logging.info(
        f"--- WGZimmer scrape complete. Found {len(all_found_rooms)} total listings. ---"
    )
    return all_found_rooms
