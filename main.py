import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.univ-eloued.dz/ar/ads/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = os.getenv("CHANNELS", "").split(",")

LAST_FILE = "last_post.txt"


def get_latest_post():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        if "/ads/" not in href and "/post/" not in href:
            continue

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        if href.startswith("/"):
            href = "https://www.univ-eloued.dz" + href

        print("Found:", title)
        print("URL:", href)

        return title, href

    print("No announcement found")
    return None, None


def send_telegram(title, link):

    message = f"""📢 إعلان جديد - جامعة الوادي

{title}

🔗 الرابط:
{link}
"""

    for channel in CHANNELS:

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": channel,
                "text": message
            },
            timeout=30
        )


def main():

    title, link = get_latest_post()

    if link:
        send_telegram(title, link)


if __name__ == "__main__":
    main()
