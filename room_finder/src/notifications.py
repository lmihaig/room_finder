import requests
from . import config


def send_notification(title, content, tags=""):
    """
    Sends a push notification using ntfy.sh.
    """
    headers = {"Title": title.encode("utf-8")}
    if tags:
        headers["Tags"] = tags

    try:
        requests.post(
            config.NTFY_CHANNEL,
            data=content.encode("utf-8"),
            headers=headers,
            timeout=10,
        )
    except Exception as e:
        print(f"Error sending notification: {e}")
