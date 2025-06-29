# Zurich Room Finder & Notifier

A 24/7 monitor for new room listings on WOKO and WGZimmer.ch. Get instant notifications to be one of the first to apply.

##### IMPORTANT: this tool does not automatically apply for you

## Features

- **Constant Monitoring**: Runs 24/7, checking for new rooms every few minutes (configurable).
- **Instant Notifications**: Uses the free [ntfy.sh](https://ntfy.sh/) service for alerts.
- **Smart Memory**: Remembers sent listings to prevent duplicates.
- **Private**: Runs locally; your search is your own.

---

## How to Run

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) must be installed and running.

### Step 1: Configure Notifications

1. **Choose a private topic name** on [ntfy.sh](https://ntfy.sh/) (e.g., `my-zurich-hunt-a5b7c`).
2. **Subscribe to your topic** in the ntfy mobile/desktop app.
3. **Edit the config file**: In `room_finder/src/config.py`, find the `NTFY_CHANNEL` line and replace `room_finder` with your chosen topic name.

    ```python
    # Before
    NTFY_CHANNEL = "https://ntfy.sh/room_finder"
    
    # After
    NTFY_CHANNEL = "https://ntfy.sh/my-zurich-hunt-a5b7c"
    ```

4. You can also adjust `CITIES_TO_SEARCH_BY_NAME` and `WGZIMMER_SEARCH_CRITERIA_BASE` in the same file to narrow your search.

### Step 2: Start the Service

1. Open a terminal in the project's root directory.
2. Run the command:

    ```bash
    docker compose up -d --build
    ```

    The service will build and start running in the background.

---

## Managing the Service

- **Check Status (View Logs):**

    ```bash
    docker compose logs -f
    ```

    *(Press `Ctrl+C` to stop viewing logs without stopping the service.)*

- **Stop the Service:**

    ```bash
    docker compose down
    ```
