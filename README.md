# E-Commerce Arbitrage Bot for 2026

A fully automated Python bot for finding and executing profitable arbitrage opportunities between Amazon/Walmart and eBay/Shopify.

## 🚀 Features

- **Multi-Source Scraping**: Scrapes product prices and stock from Amazon and Walmart using BeautifulSoup + requests
- **Stealth Mode**: Implements user-agent rotation, random delays, and proxy support to avoid detection
- **Smart Filtering**: Automatically filters products with >20% profit margin after fees/shipping
- **High-Demand Detection**: Identifies trending products using keyword matching
- **Automated Listing**: Auto-posts profitable items to eBay using the eBay SDK
- **Real-Time Alerts**: Telegram notifications for hot deals and stock drops
- **Risk Management**: Built-in limits for daily spending and listing caps
- **Full Async**: Asynchronous execution with automatic error retries
- **Database Tracking**: SQLite database for tracking items and inventory

## 📋 Prerequisites

- Python 3.8+
- eBay Developer Account (for API access)
- Telegram Bot Token (optional, for notifications)
- Residential proxies (optional, for better scraping)

## 🔧 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/brownjake9888-ai/ecommerce-arbitrage-bot.git
cd ecommerce-arbitrage-bot
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## ⚙️ Configuration

Edit the `.env` file with your credentials:

### Telegram Configuration (Optional)
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### eBay API Configuration
```
EBAY_APP_ID=your_ebay_app_id
EBAY_DEV_ID=your_ebay_dev_id
EBAY_CERT_ID=your_ebay_cert_id
EBAY_AUTH_TOKEN=your_ebay_auth_token
EBAY_SANDBOX=False  # Set to True for testing
```

### Risk Limits
```
MAX_BUY_AMOUNT=500          # Maximum daily spending
DAILY_LISTINGS_CAP=20       # Maximum listings per day
MIN_PROFIT_MARGIN=0.20      # Minimum 20% profit margin
```

### Scraping Configuration
```
SCRAPE_DELAY_MIN=2          # Minimum delay between requests (seconds)
SCRAPE_DELAY_MAX=5          # Maximum delay between requests (seconds)
```

### Proxy Configuration (Optional)
```
PROXY_LIST=http://proxy1:port,http://proxy2:port
PROXY_AUTH=username:password
```

## 🎯 Usage

### Basic Usage

1. **Edit `bot.py` to add product URLs:**
```python
urls = [
    'https://www.amazon.com/dp/PRODUCT_ID',
    'https://www.walmart.com/ip/product-name/12345',
]
```

2. **Run the bot once:**
```bash
python bot.py
```

3. **Run continuously (monitoring mode):**
Edit `bot.py` and uncomment:
```python
await bot.run_continuous(urls, interval_minutes=60)
```

### Advanced Usage

**Custom profit margin:**
```python
bot = ArbitrageBot()
bot.filter.min_profit_margin = 0.25  # 25% minimum margin
```

**Custom listing limits:**
```python
await bot.create_listings(max_listings=10)
```

## 📁 Project Structure

```
ecommerce-arbitrage-bot/
├── bot.py                  # Main bot orchestrator
├── scraper.py              # Amazon/Walmart scraping logic
├── stealth.py              # User-agent rotation, delays, proxies
├── filter.py               # Product filtering logic
├── profit_calculator.py    # Fee and profit calculations
├── ebay_lister.py         # eBay listing automation
├── telegram_notifier.py    # Telegram notifications
├── database.py             # SQLite database management
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment file
└── README.md              # This file
```

## 🛡️ Stealth Features

The bot includes multiple stealth mechanisms:

- **User-Agent Rotation**: Random user agents for each request
- **Random Delays**: Variable delays between requests (2-5 seconds)
- **Proxy Support**: Rotate through residential proxies
- **Header Spoofing**: Realistic browser headers
- **Request Throttling**: Built-in rate limiting

## 💰 Profit Calculation

The bot automatically calculates:
- eBay final value fees (12.9%)
- Payment processing fees (3.49% + $0.49)
- Estimated shipping costs
- Net profit and profit margin

## 📊 Database Schema

### tracked_items
- Product information from source sites
- Price tracking and profit margins
- Stock status monitoring

### inventory
- Items ready for or already listed
- Purchase and listing prices
- Sale tracking

### daily_stats
- Daily listing counts
- Total spending tracking
- Performance metrics

## 🔔 Telegram Notifications

The bot sends notifications for:
- 🔥 Hot deals (>30% profit margin)
- ✅ Successful listings created
- 📦 Stock alerts (out-of-stock items back in stock)
- ⚠️ Errors and warnings
- 📊 Daily summary statistics

## ⚠️ Legal & Ethical Considerations

1. **Terms of Service**: Ensure scraping complies with Amazon/Walmart ToS
2. **Rate Limiting**: Respect website rate limits to avoid IP bans
3. **Product Rights**: Only list products you have the right to sell
4. **Taxes**: Report all income and pay applicable taxes
5. **eBay Policies**: Follow all eBay selling policies

## 🐛 Troubleshooting

**Bot can't scrape products:**
- Check if you're being blocked (try proxies)
- Verify product URLs are correct
- Check internet connection

**eBay listings fail:**
- Verify eBay API credentials
- Check if sandbox mode is correct
- Review eBay API error messages

**No profitable products found:**
- Adjust `MIN_PROFIT_MARGIN` in `.env`
- Add more product URLs to monitor
- Check if prices have changed

## 📈 Future Enhancements

- [ ] Shopify integration
- [ ] Machine learning for price prediction
- [ ] Multiple marketplace support
- [ ] Automated image downloading
- [ ] Competition analysis
- [ ] Historical price tracking
- [ ] Auto-repricing based on competition

## 📝 License

This project is for educational purposes only. Use responsibly and ensure compliance with all applicable laws and terms of service.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚡ Performance Tips

1. **Use residential proxies** for better scraping success rates
2. **Monitor fewer products** initially to avoid rate limits
3. **Adjust delays** based on your proxy quality
4. **Use sandbox mode** when testing eBay integration
5. **Start with higher profit margins** (25-30%) while learning

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Disclaimer**: This bot is provided as-is for educational purposes. Users are responsible for ensuring compliance with all applicable laws, regulations, and website terms of service.