"""Product filtering logic based on profit margin and keywords."""
import logging
from typing import Dict, List
from config import MIN_PROFIT_MARGIN, HIGH_DEMAND_KEYWORDS
from profit_calculator import ProfitCalculator

logger = logging.getLogger(__name__)


class ProductFilter:
    """Filters products based on profitability and demand."""
    
    def __init__(self, min_profit_margin: float = MIN_PROFIT_MARGIN):
        """Initialize product filter."""
        self.min_profit_margin = min_profit_margin
        self.profit_calculator = ProfitCalculator()
        self.high_demand_keywords = HIGH_DEMAND_KEYWORDS
    
    def has_high_demand_keyword(self, title: str) -> bool:
        """Check if product title contains high-demand keywords."""
        title_lower = title.lower()
        for keyword in self.high_demand_keywords:
            if keyword.lower() in title_lower:
                return True
        return False
    
    def estimate_market_price(self, source_price: float) -> float:
        """Estimate market/resale price based on source price."""
        # Simple heuristic: typically 30-50% markup for resale
        # This should ideally be replaced with actual market research
        markup_multiplier = 1.4
        return source_price * markup_multiplier
    
    def filter_product(self, product_data: Dict, platform: str = 'ebay') -> Dict:
        """Filter and evaluate a product."""
        if not product_data:
            return None
        
        # Check if product has required fields
        if 'price' not in product_data or 'title' not in product_data:
            logger.warning("Product missing required fields")
            return None
        
        # Check if product is in stock
        if not product_data.get('in_stock', False):
            logger.debug(f"Product out of stock: {product_data.get('title', 'Unknown')}")
            return None
        
        purchase_price = product_data['price']
        estimated_sale_price = self.estimate_market_price(purchase_price)
        
        # Calculate profit
        profit_info = self.profit_calculator.calculate_profit(
            purchase_price, 
            estimated_sale_price, 
            platform
        )
        
        # Check profit margin
        if profit_info['profit_margin'] < self.min_profit_margin:
            logger.debug(
                f"Product below minimum margin: {product_data.get('title', 'Unknown')} "
                f"({profit_info['profit_margin']:.2%} < {self.min_profit_margin:.2%})"
            )
            return None
        
        # Check high demand keywords
        has_keyword = self.has_high_demand_keyword(product_data.get('title', ''))
        
        # Build filtered product data
        filtered_product = {
            **product_data,
            'estimated_sale_price': estimated_sale_price,
            'profit_info': profit_info,
            'has_high_demand_keyword': has_keyword,
            'is_profitable': True
        }
        
        logger.info(
            f"✓ Profitable product found: {product_data.get('title', 'Unknown')} - "
            f"Margin: {profit_info['profit_margin']:.2%}, Profit: ${profit_info['profit']:.2f}"
        )
        
        return filtered_product
    
    def filter_multiple(self, products: List[Dict], platform: str = 'ebay') -> List[Dict]:
        """Filter multiple products."""
        filtered = []
        for product in products:
            result = self.filter_product(product, platform)
            if result:
                filtered.append(result)
        
        logger.info(f"Filtered {len(filtered)} profitable products from {len(products)} total")
        return filtered
    
    def rank_by_profitability(self, products: List[Dict]) -> List[Dict]:
        """Rank products by profit margin."""
        return sorted(
            products, 
            key=lambda p: p.get('profit_info', {}).get('profit_margin', 0),
            reverse=True
        )
