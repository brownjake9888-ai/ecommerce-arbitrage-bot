"""Web scraper for Amazon and Walmart product data."""
import re
import logging
import asyncio
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import requests
import aiohttp
from stealth import StealthManager

logger = logging.getLogger(__name__)


class Scraper:
    """Web scraper for e-commerce sites."""
    
    def __init__(self):
        """Initialize scraper with stealth features."""
        self.stealth = StealthManager()
        
    def scrape_amazon(self, url: str) -> Optional[Dict]:
        """Scrape product data from Amazon."""
        try:
            headers = self.stealth.get_headers()
            proxies = self.stealth.get_proxy()
            
            self.stealth.sync_random_delay()
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract product data
            product_data = {
                'source': 'amazon',
                'url': url
            }
            
            # Title
            title_elem = soup.find('span', {'id': 'productTitle'})
            if title_elem:
                product_data['title'] = title_elem.get_text().strip()
            
            # Price
            price_elem = soup.find('span', {'class': 'a-price-whole'})
            if price_elem:
                price_text = price_elem.get_text().strip()
                product_data['price'] = float(re.sub(r'[^0-9.]', '', price_text))
            
            # Stock status
            availability_elem = soup.find('div', {'id': 'availability'})
            if availability_elem:
                availability_text = availability_elem.get_text().strip()
                product_data['in_stock'] = 'in stock' in availability_text.lower()
            else:
                product_data['in_stock'] = False
            
            # Image
            image_elem = soup.find('img', {'id': 'landingImage'})
            if image_elem:
                product_data['image_url'] = image_elem.get('src', '')
            
            # Product ID (ASIN)
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            if asin_match:
                product_data['product_id'] = asin_match.group(1)
            
            logger.info(f"Scraped Amazon product: {product_data.get('title', 'Unknown')}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping Amazon: {e}")
            return None
    
    def scrape_walmart(self, url: str) -> Optional[Dict]:
        """Scrape product data from Walmart."""
        try:
            headers = self.stealth.get_headers()
            proxies = self.stealth.get_proxy()
            
            self.stealth.sync_random_delay()
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract product data
            product_data = {
                'source': 'walmart',
                'url': url
            }
            
            # Title
            title_elem = soup.find('h1', {'itemprop': 'name'})
            if title_elem:
                product_data['title'] = title_elem.get_text().strip()
            
            # Price
            price_elem = soup.find('span', {'itemprop': 'price'})
            if not price_elem:
                price_elem = soup.find('span', {'class': re.compile(r'price-characteristic')})
            
            if price_elem:
                price_text = price_elem.get_text().strip()
                product_data['price'] = float(re.sub(r'[^0-9.]', '', price_text))
            
            # Stock status
            stock_elem = soup.find('div', {'class': re.compile(r'prod-ProductOffer')})
            if stock_elem:
                stock_text = stock_elem.get_text().lower()
                product_data['in_stock'] = 'out of stock' not in stock_text
            else:
                product_data['in_stock'] = True
            
            # Image
            image_elem = soup.find('img', {'class': re.compile(r'hover-zoom-hero-image')})
            if image_elem:
                product_data['image_url'] = image_elem.get('src', '')
            
            # Product ID
            id_match = re.search(r'/ip/[^/]+/(\d+)', url)
            if id_match:
                product_data['product_id'] = id_match.group(1)
            
            logger.info(f"Scraped Walmart product: {product_data.get('title', 'Unknown')}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping Walmart: {e}")
            return None
    
    async def scrape_async(self, url: str) -> Optional[Dict]:
        """Async scraping method."""
        # Determine source from URL
        if 'amazon.com' in url:
            return await asyncio.to_thread(self.scrape_amazon, url)
        elif 'walmart.com' in url:
            return await asyncio.to_thread(self.scrape_walmart, url)
        else:
            logger.warning(f"Unknown source for URL: {url}")
            return None
    
    async def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_async(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
        
        return valid_results
