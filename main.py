import os
import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.univ-eloued.dz/ar/ads/"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNELS = os.environ["CHANNELS"]

OLD_FILE = "last_post.json"


def get_latest_post():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    response.encoding = "utf-8"

    print("حالة الموقع:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")


    # البحث عن إعلانات المستجدات
    for p in soup.find_all("p"):

        link = p.find("a", href=True)

        if link:

            title = link.text.strip()
            href = link["href"]


            # التأكد أنه إعلان من الجامعة
            if (
                title
                and "https://www.univ-eloued.dz/ar/" in href
                and "our-policies" not in href
            ):

                span = p.find("span")

                date = ""

                if span:
                    date = span.text.strip()


                return {
                    "title": title,
                    "link": href,
                    "date": date
                }


    return None



def load_old_post():

    try:

        with open(
            OLD_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return None



def save_post(post):

    with open(
        OLD_FILE,
        "w",
        encoding="utf-8"
    ) as f:

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
            "chat_id": CHANNELS,
            "text": message
        }
    )



print("بدء البحث عن المستجدات...")


latest = get_latest_post()


print("النتيجة:")
print(latest)



if latest:

    old = load_old_post()

    if latest != old:

        send_telegram(latest)

        save_post(latest)
