import requests

URL = "https://www.univ-eloued.dz/ar/ads/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
response.encoding = "utf-8"

html = response.text

print("الحالة:", response.status_code)

print("هل يوجد منصات دفع الحقوق؟")
print("منصات دفع الحقوق" in html)

print("هل يوجد frais2026؟")
print("frais2026" in html)


# استخراج جزء الإعلان إن وجد
pos = html.find("frais2026")

if pos != -1:
    print(html[pos-500:pos+500])
