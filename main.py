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

    candidates = []

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()
        title = a.get_text(" ", strip=True)

        if not title:
            continue

        if href.startswith("/"):
            href = "https://www.univ-eloued.dz" + href

        # تجاهل صفحات الإعلانات نفسها
        if href.rstrip("/") in (
            "https://www.univ-eloued.dz/ar/ads",
            "https://www.univ-eloued.dz/en/ads",
            "https://www.univ-eloued.dz/fr/ads",
        ):
            continue

        # تجاهل روابط الأقسام والصفحات العامة
        if "/ar/" not in href and "/en/" not in href and "/fr/" not in href:
            continue

        if href.endswith("/ar/") or href.endswith("/en/") or href.endswith("/fr/"):
            continue

        # حذف التكرار
        if (title, href) not in candidates:
            candidates.append((title, href))

    if not candidates:
        print("No announcement found")
        return None, None

    # العربية أولاً
    for title, href in candidates:
        if "/ar/" in href:
            print("Found (AR):", title)
            print("URL:", href)
            return title, href

    # الإنجليزية ثانياً
    for title, href in candidates:
        if "/en/" in href:
            print("Found (EN):", title)
            print("URL:", href)
            return title, href

    # الفرنسية أخيراً
    for title, href in candidates:
        if "/fr/" in href:
            print("Found (FR):", title)
            print("URL:", href)
            return title, href

    print("Found:", candidates[0][0])
    print("URL:", candidates[0][1])

    return candidates[0]


def read_last():

    if not os.path.exists(LAST_FILE):
        return ""

    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_last(link):

    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(link)


def send_telegram(title, link):

    message = f"""📢 إعلان جديد - جامعة الوادي

{title}

🔗 الرابط:
{link}
"""

    for channel in CHANNELS:

        channel = channel.strip()

        if not channel:
            continue

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": channel,
                "text": message
            },
            timeout=30
        )

        print("Sent to:", channel)


def main():

    print("Starting monitor...")

    if not BOT_TOKEN:
        print("BOT_TOKEN missing")
        return

    title, link = get_latest_post()

    if not link:
        return

    last = read_last()

    if link == last:
        print("No new announcement")
        return

    send_telegram(title, link)

    save_last(link)

    print("Done")


if __name__ == "__main__":
    main()
