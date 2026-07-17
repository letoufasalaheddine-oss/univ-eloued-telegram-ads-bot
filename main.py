import os
import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.univ-eloued.dz/ar/ads/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = os.getenv("CHANNELS", "").split(",")

OLD_FILE = "last_post.txt"


def get_latest_post():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.encoding = "utf-8"

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    post = soup.find(
        "h3",
        class_="entry-title"
    )


    if not post:
        return None


    link = post.find(
        "a",
        href=True
    )


    if not link:
        return None


    title = link.text.strip()
    url = link["href"]


    date = ""

    parent = post.find_parent(
        "div",
        class_="rt-detail"
    )


    if parent:

        date_tag = parent.find(
            "span",
            class_="date"
        )

        if date_tag:
            date = date_tag.text.strip()


    return {
        "title": title,
        "link": url,
        "date": date
    }



def load_sent_posts():

    try:

        with open(
            OLD_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return []



def save_post(post):

    posts = load_sent_posts()

    posts.append(post)


    with open(
        OLD_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            posts,
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


    for channel in CHANNELS:

        channel = channel.strip()

        if channel:

            requests.post(
                telegram_url,
                data={
                    "chat_id": channel,
                    "text": message
                },
                timeout=30
            )



def main():

    print("بدء البحث عن المستجدات...")


    latest = get_latest_post()


    print(latest)


    if latest:

        sent_posts = load_sent_posts()


        if latest not in sent_posts:

            print("إعلان جديد، يتم الإرسال...")

            send_telegram(latest)

            save_post(latest)

        else:

            print("هذا الإعلان تم نشره سابقا.")



if __name__ == "__main__":
    main()
