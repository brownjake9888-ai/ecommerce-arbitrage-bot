"""Configuration management for the arbitrage bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# eBay API Configuration
EBAY_APP_ID = os.getenv('EBAY_APP_ID')
EBAY_DEV_ID = os.getenv('EBAY_DEV_ID')
EBAY_CERT_ID = os.getenv('EBAY_CERT_ID')
EBAY_AUTH_TOKEN = os.getenv('EBAY_AUTH_TOKEN')
EBAY_SANDBOX = os.getenv('EBAY_SANDBOX', 'False') == 'True'

# Shopify Configuration
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET')
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Proxy Configuration
PROXY_LIST = os.getenv('PROXY_LIST', '').split(',') if os.getenv('PROXY_LIST') else []
PROXY_AUTH = os.getenv('PROXY_AUTH')

# Risk Limits
MAX_BUY_AMOUNT = float(os.getenv('MAX_BUY_AMOUNT', '500'))
DAILY_LISTINGS_CAP = int(os.getenv('DAILY_LISTINGS_CAP', '20'))
MIN_PROFIT_MARGIN = float(os.getenv('MIN_PROFIT_MARGIN', '0.20'))

# Scraping Configuration
SCRAPE_DELAY_MIN = int(os.getenv('SCRAPE_DELAY_MIN', '2'))
SCRAPE_DELAY_MAX = int(os.getenv('SCRAPE_DELAY_MAX', '5'))

# Database
DB_PATH = 'arbitrage.db'

# High demand keywords
HIGH_DEMAND_KEYWORDS = [
    'gaming', 'headphones', 'smartwatch', 'tablet', 'drone',
    'camera', 'speaker', 'console', 'laptop', 'phone',
    'fitness', 'airpods', 'iphone', 'samsung', 'nintendo'
]
