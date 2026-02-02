"""Telegram notification system for hot deals."""
import logging
import asyncio
from typing import Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends notifications via Telegram."""
    
    def __init__(self):
        """Initialize Telegram bot."""
        self.bot = None
        self.chat_id = TELEGRAM_CHAT_ID
        self.initialized = False
        
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            try:
                self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
                self.initialized = True
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
        else:
            logger.warning("Telegram credentials not configured")
    
    async def send_message(self, message: str) -> bool:
        """Send a text message via Telegram."""
        if not self.initialized:
            logger.debug("Telegram not initialized - skipping notification")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Telegram notification sent successfully")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def notify_hot_deal(self, product_data: Dict):
        """Send notification about a hot deal."""
        profit_info = product_data.get('profit_info', {})
        
        message = f"""
🔥 <b>HOT DEAL ALERT!</b> 🔥

<b>{product_data.get('title', 'Unknown Product')}</b>

💰 <b>Purchase Price:</b> ${product_data.get('price', 0):.2f}
💵 <b>Estimated Sale Price:</b> ${product_data.get('estimated_sale_price', 0):.2f}
📈 <b>Profit Margin:</b> {profit_info.get('profit_margin', 0):.1%}
💸 <b>Estimated Profit:</b> ${profit_info.get('profit', 0):.2f}

🏪 <b>Source:</b> {product_data.get('source', 'Unknown').title()}
🔗 <b>URL:</b> {product_data.get('url', 'N/A')}

✅ In Stock: {product_data.get('in_stock', False)}
🎯 High Demand: {product_data.get('has_high_demand_keyword', False)}
        """.strip()
        
        await self.send_message(message)
    
    async def notify_listing_created(self, product_data: Dict, listing_id: str, platform: str):
        """Send notification when a listing is created."""
        message = f"""
✅ <b>Listing Created!</b>

<b>{product_data.get('title', 'Product')}</b>

🏪 <b>Platform:</b> {platform.title()}
🆔 <b>Listing ID:</b> {listing_id}
💵 <b>Listed at:</b> ${product_data.get('estimated_sale_price', 0):.2f}
        """.strip()
        
        await self.send_message(message)
    
    async def notify_stock_drop(self, product_data: Dict):
        """Send notification about stock becoming available."""
        message = f"""
📦 <b>Stock Alert!</b>

<b>{product_data.get('title', 'Product')}</b> is now back in stock!

💰 <b>Price:</b> ${product_data.get('price', 0):.2f}
🔗 <b>URL:</b> {product_data.get('url', 'N/A')}
        """.strip()
        
        await self.send_message(message)
    
    async def notify_error(self, error_message: str):
        """Send notification about an error."""
        message = f"⚠️ <b>Error:</b> {error_message}"
        await self.send_message(message)
    
    async def notify_daily_summary(self, stats: Dict):
        """Send daily summary statistics."""
        message = f"""
📊 <b>Daily Summary</b>

📝 <b>Listings Created:</b> {stats.get('listings_created', 0)}
💰 <b>Total Spent:</b> ${stats.get('total_spent', 0):.2f}
🎯 <b>Tracked Items:</b> {stats.get('tracked_items', 0)}
        """.strip()
        
        await self.send_message(message)
