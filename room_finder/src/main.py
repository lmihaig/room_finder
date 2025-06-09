# src/main.py
import time
import sys
import logging
from . import config
from .logging_config import setup_logging
from .notifications import send_notification
from .scrapers.woko import scrape_woko
from .scrapers.wgzimmer import scrape_wgzimmer


def process_listings(listings: list, listed_ids: set):
    """
    Checks a list of scraped items against the set of already seen IDs,
    sends notifications for new items, and returns the set of newly added IDs.
    """
    newly_added_ids = set()
    if not listings:
        return newly_added_ids

    new_listings = [item for item in listings if item["id"] not in listed_ids]

    if new_listings:
        logging.info(f"Found {len(new_listings)} new listings!")
        for item in new_listings:
            if (
                item["source"] == "WOKO"
                and config.IGNORE_SUBLET
                and "Sublet" in item["title"]
            ):
                logging.info(f"Ignoring WOKO sublet: {item['title']}")
                continue

            logging.info(f"Notifying for: {item['title']}")
            tag = "house" if item["source"] == "WOKO" else "bed"
            send_notification(
                f"New room from {item['source']}: {item['title']}",
                item["details"],
                tags=tag,
            )
            newly_added_ids.add(item["id"])
    else:
        logging.info("No new listings found in this batch.")

    return newly_added_ids


def main():
    """
    Main execution loop to run the scrapers on their individual timers.
    """
    # Setup logging first
    setup_logging()

    listed_ids = set()
    last_woko_scrape_time = 0
    last_wgzimmer_scrape_time = 0
    last_heartbeat_time = time.time()

    start_message = f"Additional info: {sys.argv[1]}" if len(sys.argv) > 1 else ""
    send_notification(
        "✅ Scraper Started",
        f"WOKO every {config.WOKO_WAIT_TIME}s, WGZimmer every {config.WGZIMMER_WAIT_TIME}s. {start_message}",
        tags="rocket",
    )

    while True:
        now = time.time()

        # --- WOKO Scraper Schedule ---
        if now - last_woko_scrape_time > config.WOKO_WAIT_TIME:
            try:
                woko_listings = scrape_woko()
                new_ids = process_listings(woko_listings, listed_ids)
                listed_ids.update(new_ids)
            except Exception as e:
                logging.critical("WOKO scraper failed catastrophically!", exc_info=True)
                send_notification(
                    "❌ CRITICAL ERROR: WOKO",
                    f"The WOKO scraper has crashed: {e}",
                    tags="rotating_light",
                )
            finally:
                last_woko_scrape_time = time.time()

        # --- WGZimmer Scraper Schedule ---
        if now - last_wgzimmer_scrape_time > config.WGZIMMER_WAIT_TIME:
            try:
                wgzimmer_listings = scrape_wgzimmer()
                new_ids = process_listings(wgzimmer_listings, listed_ids)
                listed_ids.update(new_ids)
            except Exception as e:
                logging.critical(
                    "WGZimmer scraper failed catastrophically!", exc_info=True
                )
                send_notification(
                    "❌ CRITICAL ERROR: WGZimmer",
                    f"The WGZimmer scraper has crashed: {e}",
                    tags="rotating_light",
                )
            finally:
                last_wgzimmer_scrape_time = time.time()

        # --- Heartbeat Schedule ---
        if now - last_heartbeat_time > config.HEARTBEAT_EVERY:
            logging.info("Sending heartbeat notification...")
            send_notification(
                "❤️ Scraper Heartbeat",
                "The application is still up and running.",
                tags="stopwatch",
            )
            last_heartbeat_time = time.time()

        # Sleep for a short duration to prevent the loop from using 100% CPU
        time.sleep(1)


if __name__ == "__main__":
    main()
