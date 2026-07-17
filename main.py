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

    # اختبار محتوى الصفحة
    print("PAGE TITLE:")
    print(soup.title)

    print("\nPAGE TEXT:")
    print(soup.get_text(" ", strip=True)[:1000])


    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        if href.startswith("/"):
            href = "https://www.univ-eloued.dz" + href

        print("\nFOUND LINK:")
        print(title)
        print(href)

        return title, href


    print("No announcement found")
    return None, None



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

📝 {title}

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


    print("\nRESULT:")
    print(title)
    print(link)


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
