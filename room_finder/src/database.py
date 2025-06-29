# room_finder/src/database.py
import sqlite3
import logging
from . import config
from contextlib import contextmanager


@contextmanager
def db_connection():
    """Context manager for a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        yield conn
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def initialize_database():
    """
    Initializes the database and creates the 'listings' table if it
    doesn't already exist.
    """
    with db_connection() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                # Use TEXT for the ID since we are storing URLs/unique strings
                # The UNIQUE constraint prevents duplicate entries and helps with lookups.
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS listings (
                        id TEXT PRIMARY KEY,
                        source TEXT NOT NULL,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logging.info("Database initialized successfully.")
            except sqlite3.Error as e:
                logging.error(f"Error initializing database table: {e}")


def is_listing_new(listing_id: str) -> bool:
    """
    Checks if a listing ID is already present in the database.

    Args:
        listing_id: The unique identifier of the listing.

    Returns:
        True if the listing is new (not in the database), False otherwise.
    """
    with db_connection() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM listings WHERE id = ?", (listing_id,))
                return cursor.fetchone() is None
            except sqlite3.Error as e:
                logging.error(f"Error checking listing ID {listing_id}: {e}")
                # Fail-safe: assume it's not new to avoid spamming notifications
                return False
    # If connection fails, assume not new
    return False


def add_listing(listing_id: str, source: str):
    """
    Adds a new listing's ID to the database.

    Args:
        listing_id: The unique identifier of the listing.
        source: The source of the listing (e.g., 'WOKO', 'WGZimmer').
    """
    with db_connection() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                # 'OR IGNORE' ensures that if the ID already exists, it doesn't raise an error.
                cursor.execute(
                    "INSERT OR IGNORE INTO listings (id, source) VALUES (?, ?)",
                    (listing_id, source),
                )
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Error adding listing ID {listing_id}: {e}")
