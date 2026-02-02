# E-Commerce Arbitrage Bot - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
├─────────────────────────────────────────────────────────────────┤
│  bot.py (Main)  │  cli.py (CLI)  │  demo.py (Testing)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                    ArbitrageBot (bot.py)                        │
│  • Async execution                                              │
│  • Error retry logic                                            │
│  • Risk management                                              │
│  • Workflow coordination                                        │
└─────────────────────────────────────────────────────────────────┘
          │           │           │           │           │
          ▼           ▼           ▼           ▼           ▼
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│   SCRAPER    │   FILTER     │   PROFIT     │   LISTER     │  NOTIFIER    │
│              │              │  CALCULATOR  │              │              │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ scraper.py   │ filter.py    │ profit_calc  │ ebay_lister  │ telegram     │
│              │              │ ulator.py    │ .py          │ _notifier.py │
│              │              │              │              │              │
│ • Amazon     │ • Margin     │ • eBay fees  │ • SDK API    │ • Hot deals  │
│ • Walmart    │   filter     │ • Shopify    │ • Auto desc  │ • Stock      │
│ • Async      │ • Keywords   │   fees       │ • Images     │ • Errors     │
│ • Multi-URL  │ • Ranking    │ • Shipping   │ • Verify     │ • Daily sum  │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
          │           │
          ▼           ▼
┌──────────────┬──────────────┐
│   STEALTH    │   DATABASE   │
├──────────────┼──────────────┤
│ stealth.py   │ database.py  │
│              │              │
│ • User-Agent │ • SQLite     │
│ • Delays     │ • Tracked    │
│ • Proxies    │ • Inventory  │
│ • Headers    │ • Stats      │
└──────────────┴──────────────┘
          │           │
          ▼           ▼
┌──────────────┬──────────────┐
│  CONFIG      │   STORAGE    │
├──────────────┼──────────────┤
│ config.py    │ arbitrage.db │
│ .env         │ .log files   │
└──────────────┴──────────────┘
```

## Data Flow

### 1. Scraping Flow
```
URLs → Scraper → Stealth Manager → HTTP Request → Parse HTML → Product Data
```

### 2. Filtering Flow
```
Product Data → Profit Calculator → Filter → Database → Profitable Items
                                      ↓
                               Telegram Alert
```

### 3. Listing Flow
```
Profitable Items → Risk Check → eBay Lister → API Call → Listing Created
                                                             ↓
                                                    Update Database
                                                             ↓
                                                    Telegram Notify
```

### 4. Monitoring Flow
```
Tracked Items → Scraper → Compare → Stock Change? → Alert
                            ↓
                       Update Database
```

## Module Responsibilities

### Core Business Logic

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| `bot.py` | Orchestration | `run_once()`, `run_continuous()` |
| `scraper.py` | Data collection | `scrape_amazon()`, `scrape_walmart()` |
| `filter.py` | Product evaluation | `filter_product()`, `has_high_demand_keyword()` |
| `profit_calculator.py` | Financial analysis | `calculate_profit()`, `suggest_listing_price()` |
| `ebay_lister.py` | Marketplace integration | `create_listing()`, `verify_listing()` |

### Support Services

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| `stealth.py` | Anti-detection | `get_headers()`, `random_delay()`, `get_proxy()` |
| `database.py` | Persistence | `add_tracked_item()`, `add_inventory_item()` |
| `telegram_notifier.py` | Communication | `notify_hot_deal()`, `notify_stock_drop()` |
| `config.py` | Configuration | Environment variables, constants |

### User Interfaces

| Module | Purpose |
|--------|---------|
| `bot.py` | Direct execution |
| `cli.py` | Command-line interface |
| `demo.py` | Testing and demonstration |

## Database Schema

```sql
tracked_items (
    id, source, product_id, title,
    source_price, target_price, profit_margin,
    stock_status, url, image_url,
    last_checked, created_at
)

inventory (
    id, tracked_item_id, platform, listing_id,
    status, purchase_price, listing_price, profit,
    listed_at, sold_at, created_at
)

daily_stats (
    id, date, listings_created, total_spent, created_at
)
```

## Security Layers

### 1. Input Validation
- URL domain whitelisting (Amazon, Walmart only)
- Environment variable validation
- Database input sanitization

### 2. Rate Limiting
- Random delays between requests
- Daily spending caps
- Daily listing limits

### 3. Authentication
- Secure credential storage (.env)
- API token management
- Proxy authentication

### 4. Error Handling
- Try-catch blocks throughout
- Retry logic with exponential backoff
- Comprehensive logging

## Configuration System

```
.env (secrets) → config.py (loaded) → modules (imported)
```

### Configuration Categories
1. **API Credentials**: eBay, Telegram, Shopify
2. **Risk Limits**: Spending, listings, margins
3. **Scraping**: Delays, proxies, user-agents
4. **Business Logic**: Keywords, fees, thresholds

## Async Architecture

```
asyncio Event Loop
    │
    ├─ scrape_products() [concurrent scraping]
    │   └─ multiple URL requests in parallel
    │
    ├─ process_products() [sequential processing]
    │   └─ filter → save → notify
    │
    ├─ create_listings() [sequential with delays]
    │   └─ check limits → list → verify → notify
    │
    └─ monitor_stock() [concurrent monitoring]
        └─ compare old vs new data
```

## Error Recovery

```
Operation Attempt
    │
    ├─ Success → Continue
    │
    └─ Failure → Retry Logic
        │
        ├─ Attempt 1 (immediate)
        ├─ Attempt 2 (5s delay)
        └─ Attempt 3 (10s delay)
            │
            ├─ Success → Continue
            └─ Final Failure → Log & Alert
```

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Production Server           │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐ │
│  │      Python 3.8+ venv        │ │
│  │  ┌──────────────────────────┐│ │
│  │  │   Arbitrage Bot Process  ││ │
│  │  │  • Main bot loop         ││ │
│  │  │  • Database (SQLite)     ││ │
│  │  │  • Logs                  ││ │
│  │  └──────────────────────────┘│ │
│  └───────────────────────────────┘ │
│           │           │             │
│           ▼           ▼             │
│    ┌──────────┐  ┌──────────┐      │
│    │  .env    │  │ Proxies  │      │
│    │ (secret) │  │ (rotate) │      │
│    └──────────┘  └──────────┘      │
└─────────────────────────────────────┘
           │           │
           ▼           ▼
    ┌──────────┐  ┌──────────┐
    │   eBay   │  │ Telegram │
    │   API    │  │   Bot    │
    └──────────┘  └──────────┘
           │
           ▼
    ┌──────────────┐
    │ Amazon       │
    │ Walmart      │
    │ (scraping)   │
    └──────────────┘
```

## Scalability Considerations

### Current Capacity
- **Products**: Handles 100s-1000s of products
- **Requests**: 2-5 second delays = ~12-30 products/minute
- **Database**: SQLite adequate for 100K+ records

### Scaling Options
1. **Horizontal**: Multiple bot instances with different product sets
2. **Vertical**: Increase concurrent scraping (reduce delays with better proxies)
3. **Database**: Migrate to PostgreSQL for multi-instance access
4. **Caching**: Add Redis for temporary data

## Performance Optimization

### Current Optimizations
- Async I/O for concurrent operations
- Connection pooling (implicit in aiohttp)
- Database indexing on frequently queried fields
- Lazy loading of heavy dependencies

### Future Optimizations
- [ ] Implement result caching
- [ ] Use connection pooling explicitly
- [ ] Add database query optimization
- [ ] Implement background task queue

## Monitoring & Observability

### Current Monitoring
- Log files (`arbitrage_bot.log`)
- Telegram notifications
- Database statistics
- Console output

### Recommended Additions
- [ ] Metrics dashboard
- [ ] Health check endpoint
- [ ] Performance monitoring
- [ ] Alert aggregation

---

**Last Updated**: 2026-02-01
**Version**: 1.0.0
**Status**: Production Ready
