import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

def check_ticket(url, ticket_name):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/136 Safari/537.36")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"🔍 Checking {ticket_name}")
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.panel-title'))
        )

        cards = driver.find_elements(By.CSS_SELECTOR, '.row.no-gutters.align-items-center.m-0')
        for card in cards:
            try:
                label = card.find_element(By.TAG_NAME, 'p').text.strip().lower()
                if ticket_name.lower() in label:
                    btn = card.find_element(By.CSS_SELECTOR, 'a.btn-buy')
                    btn_text = btn.text.strip()
                    if "buy" in btn_text.lower():
                        msg = f"✅ {ticket_name} is AVAILABLE! – {btn_text}"
                        print(msg)
                        send_telegram_message(f"🎟️ {msg}")
                    elif "sold" in btn_text.lower():
                        print(f"❌ {ticket_name} Sold Out – {btn_text}")
                    else:
                        print(f"⚠️ {ticket_name} status unclear – {btn_text}")
                    break
            except:
                continue

    except Exception as e:
        print(f"❌ Error for {ticket_name}: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    while True:
        print("🎟️ Running ticket check...")
        check_ticket("https://singaporegp.sg/en/tickets/general-tickets/grandstands/sunday", "Stamford Grandstand")
        check_ticket("https://singaporegp.sg/en/tickets/general-tickets/walkabouts/sunday", "Zone 4 Walkabout")
        print("⏱️ Waiting 30 minutes...\n")
        time.sleep(1800)
