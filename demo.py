"""Example/demo script showing how to use the arbitrage bot."""
import asyncio
import logging
from database import Database
from profit_calculator import ProfitCalculator
from filter import ProductFilter

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_profit_calculator():
    """Demo the profit calculator."""
    print("\n" + "=" * 60)
    print("DEMO: Profit Calculator")
    print("=" * 60 + "\n")
    
    calc = ProfitCalculator()
    
    # Example scenarios
    scenarios = [
        (50.00, 95.00, "Low-cost item with good margin"),
        (100.00, 180.00, "Mid-price item"),
        (200.00, 320.00, "Higher-price item"),
    ]
    
    for purchase, sale, description in scenarios:
        result = calc.calculate_profit(purchase, sale, 'ebay')
        print(f"{description}:")
        print(f"  Purchase: ${purchase:.2f} → Sale: ${sale:.2f}")
        print(f"  Profit: ${result['profit']:.2f} ({result['profit_margin']:.1%})")
        print(f"  eBay Fees: ${result['platform_fees']:.2f}")
        print(f"  Shipping: ${result['shipping_cost']:.2f}")
        print()


async def demo_database():
    """Demo database operations."""
    print("\n" + "=" * 60)
    print("DEMO: Database Operations")
    print("=" * 60 + "\n")
    
    import os
    if os.path.exists('demo_arbitrage.db'):
        os.remove('demo_arbitrage.db')
    
    db = Database('demo_arbitrage.db')
    print("✓ Database initialized")
    
    # Add some demo items
    items = [
        ("amazon", "DEMO123", "Gaming Headphones Pro", 45.00, 89.99, 0.28),
        ("walmart", "DEMO456", "Wireless Mouse RGB", 25.00, 52.99, 0.32),
        ("amazon", "DEMO789", "USB-C Cable 6ft", 8.00, 15.99, 0.21),
    ]
    
    for source, pid, title, price, target, margin in items:
        item_id = db.add_tracked_item(
            source=source,
            product_id=pid,
            title=title,
            source_price=price,
            target_price=target,
            profit_margin=margin,
            stock_status='in_stock',
            url=f'https://example.com/{pid}',
            image_url=''
        )
        print(f"✓ Added: {title} (ID: {item_id})")
    
    # Query items
    profitable_items = db.get_tracked_items(min_profit_margin=0.25)
    print(f"\n✓ Found {len(profitable_items)} items with >25% margin:")
    for item in profitable_items:
        print(f"  - {item['title']}: {item['profit_margin']:.1%} margin")
    
    # Cleanup
    os.remove('demo_arbitrage.db')
    print()


async def demo_filter():
    """Demo product filtering."""
    print("\n" + "=" * 60)
    print("DEMO: Product Filtering")
    print("=" * 60 + "\n")
    
    filter_obj = ProductFilter(min_profit_margin=0.20)
    
    # Demo products
    products = [
        {
            'source': 'amazon',
            'product_id': 'DEMO1',
            'title': 'Apple AirPods Pro Wireless Earbuds',
            'price': 35.00,  # Low price for high-demand item
            'in_stock': True,
            'url': 'https://example.com/1',
            'image_url': ''
        },
        {
            'source': 'walmart',
            'product_id': 'DEMO2',
            'title': 'Nintendo Switch Console',
            'price': 150.00,
            'in_stock': True,
            'url': 'https://example.com/2',
            'image_url': ''
        },
    ]
    
    print("Input products:")
    for p in products:
        print(f"  - {p['title']}")
        print(f"    Source: {p['source']}, Price: ${p['price']:.2f}")
    
    # Filter them
    print(f"\nFiltering with {filter_obj.min_profit_margin:.0%} minimum margin...\n")
    filtered = filter_obj.filter_multiple(products, platform='ebay')
    
    print(f"Result: {len(filtered)} profitable products found\n")
    for p in filtered:
        profit_info = p.get('profit_info', {})
        print(f"✓ {p['title']}")
        print(f"  Purchase: ${p['price']:.2f}")
        print(f"  Estimated Sale: ${p.get('estimated_sale_price', 0):.2f}")
        print(f"  Margin: {profit_info.get('profit_margin', 0):.1%}")
        print(f"  Profit: ${profit_info.get('profit', 0):.2f}")
        print(f"  High-demand: {p.get('has_high_demand_keyword', False)}")
        print()


async def demo_bot_structure():
    """Demo bot structure (without initialization)."""
    print("\n" + "=" * 60)
    print("DEMO: Bot Structure")
    print("=" * 60 + "\n")
    
    print("The ArbitrageBot includes these components:")
    print("✓ Database - SQLite for tracking items/inventory")
    print("✓ Scraper - BeautifulSoup + requests for Amazon/Walmart")
    print("✓ Stealth - User-agent rotation, delays, proxy support")
    print("✓ Product filter - Filters by profit margin & keywords")
    print("✓ Profit calculator - Calculates fees & margins")
    print("✓ eBay lister - Automated listing creation")
    print("✓ Telegram notifier - Real-time notifications")
    
    print("\nThe bot can:")
    print("  1. Scrape products from Amazon/Walmart")
    print("  2. Filter profitable items (>20% margin)")
    print("  3. Create eBay listings automatically")
    print("  4. Send Telegram notifications")
    print("  5. Monitor stock changes")
    print("  6. Respect daily limits and risk management")
    print("\nTo initialize: Install dependencies with 'pip install -r requirements.txt'")
    print()


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print(" " * 15 + "E-COMMERCE ARBITRAGE BOT - DEMO")
    print("=" * 70)
    
    await demo_profit_calculator()
    await demo_database()
    await demo_filter()
    await demo_bot_structure()
    
    print("=" * 70)
    print("Demo completed! To use the real bot:")
    print("  1. Configure .env with your API keys")
    print("  2. Add product URLs to bot.py")
    print("  3. Run: python bot.py")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
