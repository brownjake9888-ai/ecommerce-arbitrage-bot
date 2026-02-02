"""SQLite database management for tracking items and inventory."""
import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager
from config import DB_PATH

logger = logging.getLogger(__name__)


class Database:
    """Manages SQLite database operations for the arbitrage bot."""

    def __init__(self, db_path=DB_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tracked items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    source_price REAL NOT NULL,
                    target_price REAL,
                    profit_margin REAL,
                    stock_status TEXT,
                    url TEXT,
                    image_url TEXT,
                    last_checked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, product_id)
                )
            ''')
            
            # Inventory/listings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracked_item_id INTEGER,
                    platform TEXT NOT NULL,
                    listing_id TEXT,
                    status TEXT DEFAULT 'pending',
                    purchase_price REAL,
                    listing_price REAL,
                    profit REAL,
                    listed_at TIMESTAMP,
                    sold_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tracked_item_id) REFERENCES tracked_items(id)
                )
            ''')
            
            # Daily stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    listings_created INTEGER DEFAULT 0,
                    total_spent REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")

    def add_tracked_item(self, source, product_id, title, source_price, 
                        target_price, profit_margin, stock_status, url, image_url):
        """Add or update a tracked item."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO tracked_items 
                (source, product_id, title, source_price, target_price, 
                 profit_margin, stock_status, url, image_url, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (source, product_id, title, source_price, target_price,
                  profit_margin, stock_status, url, image_url, datetime.now()))
            return cursor.lastrowid

    def get_tracked_items(self, min_profit_margin=0):
        """Get all tracked items with minimum profit margin."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tracked_items 
                WHERE profit_margin >= ? 
                ORDER BY profit_margin DESC
            ''', (min_profit_margin,))
            return [dict(row) for row in cursor.fetchall()]

    def add_inventory_item(self, tracked_item_id, platform, purchase_price, listing_price, profit):
        """Add item to inventory."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO inventory 
                (tracked_item_id, platform, purchase_price, listing_price, profit, listed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tracked_item_id, platform, purchase_price, listing_price, profit, datetime.now()))
            return cursor.lastrowid

    def update_inventory_listing(self, inventory_id, listing_id, status='active'):
        """Update inventory item with listing ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inventory 
                SET listing_id = ?, status = ?
                WHERE id = ?
            ''', (listing_id, status, inventory_id))

    def get_daily_stats(self, date=None):
        """Get daily statistics."""
        if date is None:
            date = datetime.now().date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM daily_stats WHERE date = ?
            ''', (date,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def update_daily_stats(self, listings_increment=0, spent_increment=0):
        """Update daily statistics."""
        today = datetime.now().date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_stats (date, listings_created, total_spent)
                VALUES (?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    listings_created = listings_created + ?,
                    total_spent = total_spent + ?
            ''', (today, listings_increment, spent_increment, 
                  listings_increment, spent_increment))

    def get_inventory(self, status=None):
        """Get inventory items, optionally filtered by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM inventory WHERE status = ?', (status,))
            else:
                cursor.execute('SELECT * FROM inventory')
            return [dict(row) for row in cursor.fetchall()]
