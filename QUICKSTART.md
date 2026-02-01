# Quick Start Guide

## Installation

1. **Clone and setup:**
```bash
git clone https://github.com/brownjake9888-ai/ecommerce-arbitrage-bot.git
cd ecommerce-arbitrage-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure:**
```bash
cp .env.example .env
# Edit .env with your API credentials
```

## Testing the Bot (Demo Mode)

Run the demo to see the bot components in action:
```bash
python demo.py
```

This demonstrates:
- Profit calculation with eBay fees
- Database operations
- Product filtering
- Bot structure overview

## Using the Bot

### Step 1: Get API Credentials

**eBay (Required for listing):**
1. Sign up at https://developer.ebay.com/
2. Create an app to get App ID, Dev ID, and Cert ID
3. Generate a user auth token

**Telegram (Optional but recommended):**
1. Create a bot via @BotFather on Telegram
2. Get your bot token and chat ID

### Step 2: Add Product URLs

Edit `bot.py` and add product URLs to monitor:

```python
urls = [
    'https://www.amazon.com/dp/B08EXAMPLE',
    'https://www.walmart.com/ip/example-product/12345',
]
```

### Step 3: Run the Bot

**Single run:**
```bash
python bot.py
```

**Continuous monitoring:**
Edit `bot.py` and uncomment the continuous run line:
```python
# In the main() function, replace:
await bot.run_once(urls)

# With:
await bot.run_continuous(urls, interval_minutes=60)
```

## Configuration Options

Edit `.env` to customize:

```env
# Profit requirements
MIN_PROFIT_MARGIN=0.20          # 20% minimum

# Risk limits
MAX_BUY_AMOUNT=500              # Max daily spending
DAILY_LISTINGS_CAP=20           # Max listings per day

# Scraping behavior
SCRAPE_DELAY_MIN=2              # Min delay (seconds)
SCRAPE_DELAY_MAX=5              # Max delay (seconds)
```

## What the Bot Does

1. **Scrapes** product prices from Amazon/Walmart
2. **Calculates** profit after eBay fees and shipping
3. **Filters** products with >20% profit margin
4. **Creates** eBay listings automatically
5. **Monitors** stock changes
6. **Sends** Telegram alerts for hot deals
7. **Tracks** everything in SQLite database

## Understanding the Output

The bot logs information to:
- Console (stdout)
- `arbitrage_bot.log` file

Look for:
- ✓ Profitable product found - Items meeting criteria
- Created listing - Successfully posted to eBay
- 🔥 HOT DEAL - High-profit items (via Telegram)
- Stock alert - Items back in stock

## Database

The bot creates `arbitrage.db` with:
- **tracked_items** - All scraped products
- **inventory** - Items purchased/listed
- **daily_stats** - Spending and listing counts

Query with SQLite:
```bash
sqlite3 arbitrage.db "SELECT * FROM tracked_items ORDER BY profit_margin DESC LIMIT 10;"
```

## Troubleshooting

**No profitable products found?**
- Lower MIN_PROFIT_MARGIN in .env
- Check if product prices are correct
- Try different product categories

**Scraping blocked?**
- Add residential proxies to PROXY_LIST
- Increase SCRAPE_DELAY_MIN/MAX
- Use fewer concurrent requests

**eBay listing fails?**
- Verify API credentials
- Check EBAY_SANDBOX setting
- Review eBay API error messages

## Safety Features

The bot includes:
- Daily spending limits
- Daily listing caps
- Random delays between requests
- User-agent rotation
- Proxy support
- Error retry logic

## Next Steps

1. Start with sandbox mode (EBAY_SANDBOX=True)
2. Test with 2-3 products first
3. Monitor results for a day
4. Adjust profit margins and limits
5. Scale up gradually

## Legal Notice

Ensure compliance with:
- Amazon/Walmart Terms of Service
- eBay Seller Policies
- Local tax regulations
- Product resale rights

Use responsibly and at your own risk.
