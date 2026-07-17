import os
import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.univ-eloued.dz/ar/ads/"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

OLD_FILE = "last_post.json"


def get_latest_post():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    containers = soup.find_all(
        "div",
        class_="elementor-widget-container"
    )

    for container in containers:

        # البحث عن قسم المستجدات فقط
        if "المستجدات" in container.text:

            posts = container.find_all("p")

            for post in posts:

                link = post.find("a")

                if link:
                    title = link.text.strip()
                    url = link.get("href")

                    date = post.find("span")

                    if date:
                        date = date.text.strip()
                    else:
                        date = ""

                    return {
                        "title": title,
                        "link": url,
                        "date": date
                    }

    return None


def load_old_post():
    try:
        with open(OLD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return None


def save_post(post):
    with open(OLD_FILE, "w", encoding="utf-8") as f:
        json.dump(
            post,
            f,
            ensure_ascii=False,
            indent=4
        )


def send_telegram(post):

    message = f"""
📢 مستجد جديد - جامعة الوادي

📝 {post['title']}

📅 {post['date']}

🔗 الرابط:
{post['link']}
"""

    telegram_url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )

    requests.post(
        telegram_url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


# تشغيل البرنامج

latest = get_latest_post()

if latest:

    old = load_old_post()

    if latest != old:
        send_telegram(latest)
        save_post(latest)
