import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.univ-eloued.dz/ar/ads/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = [c.strip() for c in os.getenv("CHANNELS", "").split(",") if c.strip()]

LAST_FILE = "last_post.txt"


def get_latest_post():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # البحث داخل قائمة المستجدات فقط
    posts = soup.select("div.elementor-posts-container article.elementor-post")

    if not posts:
        print("لم يتم العثور على أي مستجد.")
        return None, None

    latest = posts[0]

    a = latest.select_one("h3.elementor-post__title a")

    if not a:
        print("تعذر استخراج الإعلان.")
        return None, None

    title = a.get_text(strip=True)
    link = a["href"]

    if link.startswith("/"):
        link = "https://www.univ-eloued.dz" + link

    print("Latest:", title)
    print("Link:", link)

    return title, link


def send_telegram(title, link):

    message = f"""📢 إعلان جديد - جامعة الشهيد حمه لخضر بالوادي

📌 {title}

🔗 {link}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for channel in CHANNELS:
        try:
            response = requests.post(
                url,
                data={
                    "chat_id": channel,
                    "text": message,
                    "disable_web_page_preview": False
                },
                timeout=30
            )

            if response.status_code == 200:
                print(f"تم الإرسال إلى {channel}")
            else:
                print(f"فشل الإرسال إلى {channel}: {response.text}")

        except Exception as e:
            print(f"خطأ أثناء الإرسال إلى {channel}: {e}")


def main():

    title, link = get_latest_post()

    if not link:
        return

    last_link = ""

    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            last_link = f.read().strip()

    if link == last_link:
        print("لا يوجد مستجد جديد.")
        return

    send_telegram(title, link)

    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(link)

    print("تم إرسال المستجد الجديد.")


if __name__ == "__main__":
    main()
