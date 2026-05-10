4. Add your products to the `PRODUCTS` list in `price_tracker.py`
```python
   PRODUCTS = [
       {
           "name":         "Product Name",
           "url":          "https://example.com/product",
           "target_price": 29.99,
       },
   ]
```

5. Run
```bash
   python price_tracker.py
```

---

## Ethical Scraping

- 1 hour delay between each price check
- Retry backoff prevents hammering servers on failure
- No personal data collected
- Public product data only

---

## Technical Challenges Solved

**1. Encoding issues**
Price values contained encoding artifacts (Â£ instead of £) due to
character mismatches. Solved by stripping all non-numeric characters
and converting to float for accurate comparison.

**2. Alert spam**
Without cooldown logic, the bot would send an alert every hour as
long as the price stayed below target. Solved by tracking alert state
per product — only re-alerting if the price recovers then drops again.

**3. Silent failures**
Network errors previously crashed the entire bot. Solved with retry
logic and per-product error handling so one failed request doesn't
stop tracking the rest.
