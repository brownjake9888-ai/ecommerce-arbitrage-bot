#!/usr/bin/env python
"""Command-line interface for the arbitrage bot."""
import argparse
import asyncio
import sys


async def run_scrape(args):
    """Scrape products from URLs."""
    from bot import ArbitrageBot
    bot = ArbitrageBot()
    
    # Read URLs from file if provided
    if args.file:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    elif args.urls:
        urls = args.urls
    else:
        print("Error: Provide URLs via --urls or --file")
        sys.exit(1)
    
    print(f"Scraping {len(urls)} URLs...")
    await bot.run_once(urls)


async def run_monitor(args):
    """Run continuous monitoring."""
    from bot import ArbitrageBot
    bot = ArbitrageBot()
    
    # Read URLs from file if provided
    if args.file:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    elif args.urls:
        urls = args.urls
    else:
        print("Error: Provide URLs via --urls or --file")
        sys.exit(1)
    
    print(f"Starting continuous monitoring of {len(urls)} URLs...")
    print(f"Checking every {args.interval} minutes")
    await bot.run_continuous(urls, interval_minutes=args.interval)


async def run_list(args):
    """Create eBay listings for tracked items."""
    from bot import ArbitrageBot
    bot = ArbitrageBot()
    
    print(f"Creating up to {args.max} listings...")
    await bot.create_listings(max_listings=args.max)


async def run_stats(args):
    """Show database statistics."""
    from database import Database
    
    db = Database()
    
    # Get tracked items
    items = db.get_tracked_items()
    profitable = [i for i in items if i['profit_margin'] >= 0.20]
    
    # Get inventory
    inventory = db.get_inventory()
    active = [i for i in inventory if i['status'] == 'active']
    
    # Get daily stats
    stats = db.get_daily_stats()
    
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    print(f"\nTracked Items: {len(items)}")
    print(f"  Profitable (>20%): {len(profitable)}")
    print(f"\nInventory: {len(inventory)} items")
    print(f"  Active listings: {len(active)}")
    
    if stats:
        print(f"\nToday's Stats:")
        print(f"  Listings created: {stats['listings_created']}")
        print(f"  Total spent: ${stats['total_spent']:.2f}")
    
    if args.top:
        print(f"\nTop {args.top} Most Profitable Items:")
        top_items = sorted(items, key=lambda x: x['profit_margin'], reverse=True)[:args.top]
        for i, item in enumerate(top_items, 1):
            print(f"  {i}. {item['title'][:50]}")
            print(f"     Margin: {item['profit_margin']:.1%}, Price: ${item['source_price']:.2f}")
    
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='E-commerce Arbitrage Bot CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape products once
  python cli.py scrape --urls https://amazon.com/dp/XXXX https://walmart.com/ip/YYYY
  
  # Monitor products continuously
  python cli.py monitor --file urls.txt --interval 60
  
  # Create listings
  python cli.py list --max 10
  
  # Show statistics
  python cli.py stats --top 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape products once')
    scrape_parser.add_argument('--urls', nargs='+', help='Product URLs to scrape')
    scrape_parser.add_argument('--file', help='File containing URLs (one per line)')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor products continuously')
    monitor_parser.add_argument('--urls', nargs='+', help='Product URLs to monitor')
    monitor_parser.add_argument('--file', help='File containing URLs (one per line)')
    monitor_parser.add_argument('--interval', type=int, default=60, help='Check interval in minutes')
    
    # List command
    list_parser = subparsers.add_parser('list', help='Create eBay listings')
    list_parser.add_argument('--max', type=int, default=5, help='Maximum number of listings to create')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--top', type=int, default=10, help='Number of top items to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    if args.command == 'scrape':
        asyncio.run(run_scrape(args))
    elif args.command == 'monitor':
        asyncio.run(run_monitor(args))
    elif args.command == 'list':
        asyncio.run(run_list(args))
    elif args.command == 'stats':
        asyncio.run(run_stats(args))


if __name__ == '__main__':
    main()
