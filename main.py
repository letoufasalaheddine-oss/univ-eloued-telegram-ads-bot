import os
import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.univ-eloued.dz/ar/ads/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = os.getenv("CHANNELS", "").split(",")

LAST_FILE = "last_post.txt"


def load_posts():

    if not os.path.exists(LAST_FILE):
        return []

    try:
        with open(
            LAST_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except:
        return []


def save_posts(posts):

    with open(
        LAST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            posts,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_new_posts():

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


    posts = []


    for item in soup.find_all(
        "h3",
        class_="entry-title"
    ):

        a = item.find(
            "a",
            href=True
        )


        if not a:
            continue


        title = a.get_text(
            strip=True
        )

        link = a["href"].strip()


        posts.append(
            {
                "title": title,
                "link": link
            }
        )


    return posts



def send_telegram(post):

    message = f"""📢 مستجد جديد - جامعة الوادي

📝 {post['title']}

🔗 الرابط:
{post['link']}
"""


    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )


    for channel in CHANNELS:

        channel = channel.strip()

        if channel:

            requests.post(
                url,
                data={
                    "chat_id": channel,
                    "text": message,
                    "disable_web_page_preview": False
                },
                timeout=30
            )



def main():

    print("بدء مراقبة مستجدات جامعة الوادي...")


    old_posts = load_posts()


    old_links = {
        post["link"]
        for post in old_posts
    }


    current_posts = get_new_posts()


    new_posts = []


    for post in reversed(current_posts):

        if post["link"] not in old_links:

            new_posts.append(post)



    if not new_posts:

        print("لا توجد مستجدات جديدة.")

        return



    for post in new_posts:

        print(
            "إرسال:",
            post["title"]
        )

        send_telegram(post)



    save_posts(
        old_posts + new_posts
    )


    print(
        f"تم إرسال {len(new_posts)} مستجد."
    )



if __name__ == "__main__":
    main()
