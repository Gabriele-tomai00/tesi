import requests
from dotenv import load_dotenv
import os

# Carica le variabili dal file .env
load_dotenv()

proxy_url = os.getenv("SCRAPY_PROXY_URL")  # es. https://100.114.19.9:3128 pay attention http or https!
username = os.getenv("SCRAPY_PROXY_USER")
password = os.getenv("SCRAPY_PROXY_PASS")
print(f"username: {username}")

# Aggiunge user e password al proxy
if username and password:
    if proxy_url.startswith("http://"):
        proxy_url = proxy_url.replace("http://", f"http://{username}:{password}@")
    elif proxy_url.startswith("https://"):
        proxy_url = proxy_url.replace("https://", f"https://{username}:{password}@")
    else:
        proxy_url = f"http://{username}:{password}@{proxy_url}"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

# Test del proxy
try:
    response = requests.get("http://ipinfo.io/json", proxies=proxies, timeout=10)
    print("✅ Proxy funzionante!")
    print("🌍 IP pubblico:", response.json().get("ip"))
except Exception as e:
    print("❌ Errore:", e)
