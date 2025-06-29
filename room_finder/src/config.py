import logging
import os

NTFY_CHANNEL = "https://ntfy.sh/room_finder"

WOKO_WAIT_TIME = 300
WGZIMMER_WAIT_TIME = 1800
HEARTBEAT_EVERY = 3600

IGNORE_SUBLET = True

DATABASE_PATH = "/app/data/listings.db"

# ------------------------------------------------------------------------------
# >> EDIT THIS LIST <<
# Add or remove cities you want to search.
# - Use the special keyword "Zurich (ALL)" to include all Zurich regions automatically.
# - Otherwise, names MUST BE exactly as they appear as keys in the CITY_NAMES dictionary.
CITIES_TO_SEARCH_BY_NAME = [
    "Zurich (ALL)",
]
# ------------------------------------------------------------------------------

# Base search criteria. The 'state' (city) will be added from the list above during the scrape.
WGZIMMER_SEARCH_CRITERIA_BASE = {
    "priceMin": "200",
    "priceMax": "750",
    "permanent": "true" if IGNORE_SUBLET else "all",
    "student": "none",
    "orderBy": "@sortDate",
    "orderDir": "descending",
    "startSearchMate": "true",
    "start": "0",
}


# ------------------------------------------------------------------------------
# DON'T SCREW WITH THESE
HEADLESS_BROWSER = True

WOKO_URL = "https://www.woko.ch/en/zimmer-in-zuerich"
WGZIMMER_SEARCH_URL = "https://www.wgzimmer.ch/en/wgzimmer/search/mate.html"
WGZIMMER_BASE_URL = "https://www.wgzimmer.ch"

WGZIMMER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.wgzimmer.ch/en/wgzimmer/search/mate.html",
    "X-Requested-With": "XMLHttpRequest",
}

CITY_NAMES = {
    "Aargau": "aargau",
    "Aarau (Stadt)": "aarau",
    "Appenzell Innerrhoden": "appenzell-innerrhoden",
    "Appenzell Ausser.": "appenzell-ausser",
    "Baden": "baden",
    "Basel City": "baselstadt",
    "Basel Land": "baselland",
    "Bern": "bern",
    "Biel": "biel",
    "Brugg": "brugg",
    "Burgdorf": "burgdorf",
    "Chur": "chur",
    "Emmental": "emmental",
    "Frauenfeld": "frauenfeld",
    "Fribourg": "fribourg",
    "Jura": "jura",
    "Geneva": "genf",
    "Glarus": "glarus",
    "Graubünden": "graubunden",
    "Interlaken": "interlaken",
    "Kloten (Zürich)": "zurich-kloten",
    "Langenthal": "langenthal",
    "Langnau": "langnau",
    "Laufenburg": "laufenburg",
    "Lausanne": "lausanne",
    "Lörrach (DE)": "loerrach",
    "Lucerne": "luzern",
    "Neuchâtel": "neuenburg",
    "Nidwalden": "nidwalden",
    "Obwalden": "obwalden",
    "Olten": "olten",
    "Ostschweiz": "ostschweiz",
    "Rapperswil-Jona": "rapperswil-jona",
    "Schaffhausen": "schaffhausen",
    "Solothurn": "solothurn",
    "Schwyz": "schwyz",
    "Spiez": "spiez",
    "St. Gallen": "st-gallen",
    "Saint-Louis (FR)": "saint-louis-fr",
    "Simmental/Saanenland": "simmental-saanenland",
    "Ticino": "tessin",
    "Thun": "thun",
    "Thurgau": "thurgau",
    "Uri": "uri",
    "Vaud": "waadt",
    "Wädenswil (ZHAW)": "waedenswil",
    "Wallis": "wallis",
    "Weil am Rhein (DE)": "weil-am-rhein-de",
    "Wil": "wil",
    "Winterthur & Agglomeration": "winterthur",
    "Zug": "zug",
    "Zurich (City)": "zurich-stadt",
    "Zürich (Altstetten, Höngg)": "zurich-altstetten",
    "Zürich (Oerlikon, Seebach, Affoltern)": "zurich-oerlikon",
    "Zürich (Rund um den See)": "zurich-lake",
    "Zürich (Aeugstertal, Affoltern am Albis)": "zurich-aeugstertal",
    "Zurich (Unterland, Weinland, Limmattal)": "zurich",
    "Zürich (Oberland, Glattal)": "zurich-oberland",
    "Liechtenstein": "liechtenstein",
}
