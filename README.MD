#  Price Tracker Bot

Automatically monitors a product price and sends an email alert 
when the price drops below your target.

---

##  Features
- Checks price automatically every hour
- Sends instant email alert when price drops
- Saves full price history to CSV
- Credentials hidden safely with .env
- Works on any product page

---

##  Sample Price History

| datetime | price |
|----------|-------|
| 2026-04-29 20:39:47 | 51.77 |
| 2026-04-29 21:39:47 | 51.77 |
| 2026-04-29 22:39:47 | 49.99 |

---

##  Built With
- Python 3.13
- Requests
- BeautifulSoup4
- Smtplib
- Python-dotenv

---

##  How to Run
1. Clone the repo
2. Install dependencies:
   pip install -r requirements.txt
3. Create .env file:
   EMAIL_SENDER=your_gmail@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_RECEIVER=receiver@gmail.com
4. Set your target price in price_tracker.py
5. Run:
   python price_tracker.py

---

##  Ethical Scraping
- 1 hour delay between each price check
- No personal data collected
- Public product data only

---

##  Technical Challenge Solved
Books.toscrape.com returns prices with encoding issues (Â£ instead of £) 
due to character encoding mismatches. Solved by stripping invalid characters 
and converting prices to floats for accurate numerical comparison against 
the target price.