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
    print("هل وجد كلمة المستجدات؟", "المستجدات" in response.text)

    soup = BeautifulSoup(response.text, "html.parser")


    # البحث عن قسم المستجدات
    title = soup.find(
        lambda tag: tag.name in ["p", "strong"]
        and "المستجدات" in tag.text
    )


    if not title:
        print("لم يتم العثور على قسم المستجدات")
        return None


    container = title.find_parent(
        "div",
        class_="elementor-widget-container"
    )


    if not container:
        print("لم يتم العثور على حاوية الإعلانات")
        return None


    # استخراج أول إعلان
    for p in container.find_all("p"):

        link = p.find("a")

        if link:

            date = p.find("span")

            post = {
                "title": link.text.strip(),
                "link": link.get("href"),
                "date": date.text.strip() if date else ""
            }

            return post


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
