# src/main.py
import time
import sys
import logging
from . import config
from .logging_config import setup_logging
from .notifications import send_notification
from .scrapers.woko import scrape_woko
from .scrapers.wgzimmer import scrape_wgzimmer
from . import database  # <-- Import the new database module


def process_listings(listings: list):
    """
    Checks a list of scraped items against the database, sends notifications
    for new items, and adds them to the database.
    """
    if not listings:
        return

    new_listings_found = 0
    for item in listings:
        # Check against the database if the listing is new
        if database.is_listing_new(item["id"]):
            new_listings_found += 1
            logging.info(f"New listing found: {item['title']}")

            # The sublet filter is now primarily handled in the WOKO scraper,
            # but this serves as a good final check.
            if (
                item["source"] == "WOKO"
                and config.IGNORE_SUBLET
                and "Sublet" in item["title"]
            ):
                logging.info(f"Ignoring WOKO sublet: {item['title']}")
                # Add to DB anyway to prevent re-checking
                database.add_listing(item["id"], item["source"])
                continue

            logging.info(f"Notifying for: {item['title']}")
            tag = "house" if item["source"] == "WOKO" else "bed"
            send_notification(
                f"New room from {item['source']}: {item['title']}",
                item["details"],
                tags=tag,
            )

            # Add the new listing ID to the database so it's not sent again
            database.add_listing(item["id"], item["source"])

    if new_listings_found > 0:
        logging.info(f"Processed {new_listings_found} new listings in this batch.")
    else:
        logging.info("No new listings found in this batch.")


def main():
    """
    Main execution loop to run the scrapers on their individual timers.
    """
    # Setup logging and database first
    setup_logging()
    database.initialize_database()  # <-- Initialize the database on startup

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
                logging.info("Running WOKO scraper...")
                woko_listings = scrape_woko()
                process_listings(woko_listings)  # <-- Process using the DB
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
                logging.info("Running WGZimmer scraper...")
                wgzimmer_listings = scrape_wgzimmer()
                process_listings(wgzimmer_listings)  # <-- Process using the DB
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
