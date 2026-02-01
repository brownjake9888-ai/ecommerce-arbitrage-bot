"""Main arbitrage bot with async execution and error retries."""
import asyncio
import logging
from typing import List
from datetime import datetime

from database import Database
from scraper import Scraper
from filter import ProductFilter
from profit_calculator import ProfitCalculator
from ebay_lister import EbayLister
from telegram_notifier import TelegramNotifier
from config import MAX_BUY_AMOUNT, DAILY_LISTINGS_CAP, MIN_PROFIT_MARGIN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ArbitrageBot:
    """Main arbitrage bot orchestrator."""
    
    def __init__(self):
        """Initialize the bot components."""
        self.db = Database()
        self.scraper = Scraper()
        self.filter = ProductFilter(min_profit_margin=MIN_PROFIT_MARGIN)
        self.profit_calculator = ProfitCalculator()
        self.ebay_lister = EbayLister()
        self.telegram = TelegramNotifier()
        
        logger.info("Arbitrage bot initialized")
    
    async def scrape_products(self, urls: List[str], max_retries: int = 3) -> List[dict]:
        """Scrape products with retry logic."""
        attempt = 0
        
        while attempt < max_retries:
            try:
                logger.info(f"Scraping {len(urls)} products (attempt {attempt + 1}/{max_retries})")
                products = await self.scraper.scrape_multiple(urls)
                
                if products:
                    logger.info(f"Successfully scraped {len(products)} products")
                    return products
                
                attempt += 1
                if attempt < max_retries:
                    await asyncio.sleep(5 * attempt)  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"Error scraping products: {e}")
                attempt += 1
                if attempt < max_retries:
                    await asyncio.sleep(5 * attempt)
        
        logger.warning("Failed to scrape products after all retries")
        return []
    
    async def process_products(self, products: List[dict]):
        """Process scraped products - filter, save, notify."""
        # Filter profitable products
        profitable = self.filter.filter_multiple(products, platform='ebay')
        
        # Rank by profitability
        ranked = self.filter.rank_by_profitability(profitable)
        
        # Save to database and notify
        for product in ranked:
            try:
                # Save to database
                profit_info = product.get('profit_info', {})
                tracked_id = self.db.add_tracked_item(
                    source=product.get('source', 'unknown'),
                    product_id=product.get('product_id', ''),
                    title=product.get('title', ''),
                    source_price=product.get('price', 0),
                    target_price=product.get('estimated_sale_price', 0),
                    profit_margin=profit_info.get('profit_margin', 0),
                    stock_status='in_stock' if product.get('in_stock') else 'out_of_stock',
                    url=product.get('url', ''),
                    image_url=product.get('image_url', '')
                )
                
                # Notify about hot deals (top profit margin)
                if profit_info.get('profit_margin', 0) > 0.3:  # >30% margin
                    await self.telegram.notify_hot_deal(product)
                
                logger.info(f"Tracked item saved: {product.get('title', 'Unknown')} (ID: {tracked_id})")
                
            except Exception as e:
                logger.error(f"Error processing product: {e}")
    
    async def create_listings(self, max_listings: int = None):
        """Create eBay listings for profitable products."""
        # Check daily limits
        today_stats = self.db.get_daily_stats()
        if today_stats:
            if today_stats['listings_created'] >= DAILY_LISTINGS_CAP:
                logger.warning(f"Daily listings cap reached: {DAILY_LISTINGS_CAP}")
                return
            
            if today_stats['total_spent'] >= MAX_BUY_AMOUNT:
                logger.warning(f"Daily spending limit reached: ${MAX_BUY_AMOUNT}")
                return
        
        # Get profitable tracked items not yet listed
        tracked_items = self.db.get_tracked_items(min_profit_margin=MIN_PROFIT_MARGIN)
        
        # Filter items not yet in inventory
        existing_inventory = self.db.get_inventory()
        tracked_ids_in_inventory = {inv['tracked_item_id'] for inv in existing_inventory}
        items_to_list = [item for item in tracked_items if item['id'] not in tracked_ids_in_inventory]
        
        if not items_to_list:
            logger.info("No new items to list")
            return
        
        # Sort by profit margin and limit
        items_to_list.sort(key=lambda x: x['profit_margin'], reverse=True)
        
        if max_listings:
            items_to_list = items_to_list[:max_listings]
        
        # Create listings
        for item in items_to_list:
            try:
                # Check if we've hit daily limits
                today_stats = self.db.get_daily_stats()
                if today_stats:
                    if today_stats['listings_created'] >= DAILY_LISTINGS_CAP:
                        logger.warning("Daily listings cap reached during processing")
                        break
                    if today_stats['total_spent'] >= MAX_BUY_AMOUNT:
                        logger.warning("Daily spending limit reached during processing")
                        break
                
                # Create eBay listing
                listing_id = self.ebay_lister.create_listing(item, item['target_price'])
                
                if listing_id:
                    # Add to inventory
                    inventory_id = self.db.add_inventory_item(
                        tracked_item_id=item['id'],
                        platform='ebay',
                        purchase_price=item['source_price'],
                        listing_price=item['target_price'],
                        profit=item['target_price'] - item['source_price']
                    )
                    
                    # Update listing ID
                    self.db.update_inventory_listing(inventory_id, listing_id, 'active')
                    
                    # Update daily stats
                    self.db.update_daily_stats(
                        listings_increment=1,
                        spent_increment=item['source_price']
                    )
                    
                    # Notify
                    await self.telegram.notify_listing_created(item, listing_id, 'ebay')
                    
                    logger.info(f"Created listing {listing_id} for {item['title']}")
                    
                    # Small delay between listings
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error creating listing: {e}")
                await self.telegram.notify_error(f"Failed to create listing: {str(e)}")
    
    async def monitor_stock(self):
        """Monitor tracked items for stock changes."""
        logger.info("Monitoring stock for tracked items...")
        
        # Get tracked items
        tracked_items = self.db.get_tracked_items()
        urls = [item['url'] for item in tracked_items if item.get('url')]
        
        if not urls:
            logger.info("No items to monitor")
            return
        
        # Scrape current data
        current_data = await self.scrape_products(urls)
        
        # Check for stock changes
        for product in current_data:
            try:
                # Find corresponding tracked item
                tracked = next(
                    (item for item in tracked_items 
                     if item['product_id'] == product.get('product_id')),
                    None
                )
                
                if tracked:
                    # Check if stock status changed
                    old_status = tracked['stock_status']
                    new_status = 'in_stock' if product.get('in_stock') else 'out_of_stock'
                    
                    if old_status == 'out_of_stock' and new_status == 'in_stock':
                        # Stock became available!
                        await self.telegram.notify_stock_drop(product)
                        logger.info(f"Stock alert: {product.get('title')} back in stock!")
                    
                    # Update tracked item
                    self.db.add_tracked_item(
                        source=product.get('source', 'unknown'),
                        product_id=product.get('product_id', ''),
                        title=product.get('title', ''),
                        source_price=product.get('price', 0),
                        target_price=tracked['target_price'],
                        profit_margin=tracked['profit_margin'],
                        stock_status=new_status,
                        url=product.get('url', ''),
                        image_url=product.get('image_url', '')
                    )
                    
            except Exception as e:
                logger.error(f"Error monitoring stock: {e}")
    
    async def send_daily_summary(self):
        """Send daily summary via Telegram."""
        today_stats = self.db.get_daily_stats()
        tracked_items = len(self.db.get_tracked_items())
        
        summary = {
            'listings_created': today_stats['listings_created'] if today_stats else 0,
            'total_spent': today_stats['total_spent'] if today_stats else 0,
            'tracked_items': tracked_items
        }
        
        await self.telegram.notify_daily_summary(summary)
    
    async def run_once(self, urls: List[str]):
        """Run the bot once with given URLs."""
        try:
            logger.info("=" * 60)
            logger.info("Starting arbitrage bot cycle")
            logger.info("=" * 60)
            
            # Scrape products
            products = await self.scrape_products(urls)
            
            # Process products (filter, save, notify)
            if products:
                await self.process_products(products)
            
            # Create listings for profitable items
            await self.create_listings(max_listings=5)
            
            # Monitor existing tracked items
            await self.monitor_stock()
            
            # Send summary
            await self.send_daily_summary()
            
            logger.info("Bot cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in bot cycle: {e}")
            await self.telegram.notify_error(f"Bot cycle error: {str(e)}")
    
    async def run_continuous(self, urls: List[str], interval_minutes: int = 60):
        """Run the bot continuously with specified interval."""
        while True:
            try:
                await self.run_once(urls)
                logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
                await asyncio.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous run: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error


async def main():
    """Main entry point."""
    # Example URLs to monitor (replace with actual URLs)
    urls = [
        # Add Amazon/Walmart product URLs here
        # 'https://www.amazon.com/dp/EXAMPLE1',
        # 'https://www.walmart.com/ip/example/12345',
    ]
    
    if not urls:
        logger.warning("No URLs configured. Add product URLs to the 'urls' list in main()")
        logger.info("Example usage:")
        logger.info("  urls = ['https://www.amazon.com/dp/PRODUCT_ID', ...]")
        return
    
    bot = ArbitrageBot()
    
    # Run once
    await bot.run_once(urls)
    
    # Or run continuously (uncomment to use)
    # await bot.run_continuous(urls, interval_minutes=60)


if __name__ == '__main__':
    asyncio.run(main())
