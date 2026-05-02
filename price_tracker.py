import requests
import csv
import time
import smtplib
import os
from bs4 import BeautifulSoup
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# -- Config --
load_dotenv()
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
TARGET_URL     = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
TARGET_PRICE   = 60.00
CHECK_EVERY    = 3600

# -- Email Config --
EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# -- Get Price --
def get_price(url):
    response = requests.get(url)
    soup     = BeautifulSoup(response.text, "html.parser")
    price    = soup.select_one("p.price_color").text.strip()
    price    = float(price.replace("Â", "").replace("£", "").strip())
    return price


# -- Save Price History --
def save_price(price):
    filename   = os.path.join(BASE_DIR, "price_history.csv")
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["datetime", "price"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price":    price
        })
    print(f"Price recorded: £{price} at {datetime.now().strftime('%H:%M:%S')}")


# -- Send Alert --
def send_alert(price):
    msg            = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg["Subject"] = f"🚨 Price Alert! A Light in the Attic dropped to £{price}"

    body = f"""Good news!

The price you've been tracking has dropped!

📚 Book    : A Light in the Attic
💰 Price   : £{price}
🎯 Target  : £{TARGET_PRICE}
🕒 Time    : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Buy it now before the price goes back up!

— Price Tracker Bot 🤖"""

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print(f"Alert sent! Price dropped to £{price} 📧")


# -- Main --
def track_price():
    print(f"Tracking: {TARGET_URL}")
    print(f"Target price: £{TARGET_PRICE}")
    print(f"Checking every {CHECK_EVERY // 3600} hour(s)")
    print("-" * 50)

    while True:
        price = get_price(TARGET_URL)
        save_price(price)

        if price < TARGET_PRICE:
            print(f"🚨 Price dropped to £{price} — sending alert!")
            send_alert(price)
        else:
            print(f"Price is £{price} — above target £{TARGET_PRICE}")

        time.sleep(CHECK_EVERY)


# -- Run --
track_price()