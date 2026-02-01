"""Stealth utilities for web scraping: user-agent rotation, delays, proxy management."""
import random
import asyncio
import logging
from typing import Optional, Dict
from fake_useragent import UserAgent
from config import SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX, PROXY_LIST, PROXY_AUTH

logger = logging.getLogger(__name__)


class StealthManager:
    """Manages stealth features for web scraping."""
    
    def __init__(self):
        """Initialize stealth manager."""
        self.ua = UserAgent()
        self.proxies = PROXY_LIST if PROXY_LIST else []
        self.proxy_auth = PROXY_AUTH
        
    def get_headers(self) -> Dict[str, str]:
        """Generate randomized headers."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list."""
        if not self.proxies:
            return None
        
        proxy_url = random.choice(self.proxies)
        
        if self.proxy_auth and '@' not in proxy_url:
            # Add authentication to proxy URL
            protocol, rest = proxy_url.split('://', 1)
            proxy_url = f"{protocol}://{self.proxy_auth}@{rest}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    async def random_delay(self):
        """Add random delay between requests."""
        delay = random.uniform(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        await asyncio.sleep(delay)
    
    def sync_random_delay(self):
        """Synchronous random delay for non-async code."""
        import time
        delay = random.uniform(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
