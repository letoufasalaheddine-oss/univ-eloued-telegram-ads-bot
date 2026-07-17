import requests

URL = "https://www.univ-eloued.dz/ar/ads/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)

print("الحالة:", response.status_code)

print(response.text[:3000])
