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


    # البحث عن جميع الروابط
    links = soup.find_all("a", href=True)


    for link in links:

        title = link.text.strip()
        url = link["href"]


        # اختيار روابط الإعلانات فقط
        if (
            title
            and "/ar/" in url
            and "ads" not in url
        ):

            parent = link.find_parent("p")

            date = ""

            if parent:

                span = parent.find("span")

                if span:
                    date = span.text.strip()


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


    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


    requests.post(
        url,
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
