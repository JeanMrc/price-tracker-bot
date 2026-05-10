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

# ─────────────────────────────────────────
# Products
# ─────────────────────────────────────────
PRODUCTS = [
    {
        "name":         "A Light in the Attic",
        "url":          "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "target_price": 60.00,
    },
    {
        "name":         "Tipping the Velvet",
        "url":          "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
        "target_price": 50.00,
    },
]

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
load_dotenv()

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CHECK_EVERY   = 3600  # seconds
MAX_RETRIES   = 3
DELAY         = 2     # seconds between retries

EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ─────────────────────────────────────────
# Fetch Price
# ─────────────────────────────────────────
def get_price(url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup  = BeautifulSoup(response.text, "html.parser")
            raw   = soup.select_one("p.price_color").text.strip()
            price = float(''.join(c for c in raw if c.isdigit() or c == '.'))
            return price
        except Exception as e:
            print(f"  Attempt {attempt} failed: {e}")
            time.sleep(DELAY * attempt)
    print(f"  Could not fetch price from {url}")
    return None

# ─────────────────────────────────────────
# Save Price History
# ─────────────────────────────────────────
def save_price(product_name, price):
    safe_name  = product_name.lower().replace(" ", "_")
    filename   = os.path.join(BASE_DIR, f"{safe_name}_history.csv")
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["datetime", "price"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price":    price
        })
    print(f"  [{product_name}] £{price} recorded.")

# ─────────────────────────────────────────
# Send Alert
# ─────────────────────────────────────────
def send_alert(product):
    price = product["current_price"]
    msg            = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg["Subject"] = f"Price Alert — {product['name']} dropped to £{price}"

    body = f"""Good news!

The price you've been tracking has dropped!

Product : {product['name']}
Price   : £{price}
Target  : £{product['target_price']}
Time    : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

— Price Tracker Bot"""

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"  Alert sent for {product['name']}!")
    except Exception as e:
        print(f"  Failed to send alert: {e}")

# ─────────────────────────────────────────
# Main Tracking Loop
# ─────────────────────────────────────────
def track_prices():
    # Track which products have already been alerted
    alerted = {p["name"]: False for p in PRODUCTS}

    print("Price Tracker Started")
    print(f"Tracking {len(PRODUCTS)} product(s) — checking every {CHECK_EVERY // 3600} hour(s)")
    print("=" * 50)

    while True:
        for product in PRODUCTS:
            name  = product["name"]
            price = get_price(product["url"])

            if price is None:
                print(f"  [{name}] Skipping — could not fetch price.")
                continue

            product["current_price"] = price
            save_price(name, price)

            if price < product["target_price"]:
                if not alerted[name]:
                    print(f"  [{name}] Price dropped to £{price} — sending alert!")
                    send_alert(product)
                    alerted[name] = True
                else:
                    print(f"  [{name}] Still below target £{product['target_price']} — alert already sent.")
            else:
                print(f"  [{name}] £{price} — above target £{product['target_price']}")
                alerted[name] = False  # reset if price goes back up

        print(f"\nNext check in {CHECK_EVERY // 3600} hour(s)...\n")
        time.sleep(CHECK_EVERY)

# ─────────────────────────────────────────
# Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    track_prices()
