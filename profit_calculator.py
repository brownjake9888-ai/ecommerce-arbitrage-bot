"""Profit calculator with fee and shipping calculations."""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ProfitCalculator:
    """Calculates profit margins after fees and shipping."""
    
    # eBay fee structure (2024-2026 typical rates)
    EBAY_FINAL_VALUE_FEE = 0.129  # 12.9% final value fee
    EBAY_PAYMENT_PROCESSING = 0.0349  # 3.49% + $0.49 per transaction
    EBAY_PAYMENT_FIXED = 0.49
    
    # Estimated shipping costs (can be customized)
    SHIPPING_COST_BASE = 5.00
    SHIPPING_COST_PER_LB = 2.00
    
    # Shopify fees
    SHOPIFY_TRANSACTION_FEE = 0.029  # 2.9% + $0.30
    SHOPIFY_TRANSACTION_FIXED = 0.30
    
    def __init__(self):
        """Initialize profit calculator."""
        pass
    
    def calculate_ebay_fees(self, sale_price: float) -> Dict[str, float]:
        """Calculate eBay fees for a given sale price."""
        final_value_fee = sale_price * self.EBAY_FINAL_VALUE_FEE
        payment_fee = (sale_price * self.EBAY_PAYMENT_PROCESSING) + self.EBAY_PAYMENT_FIXED
        total_fees = final_value_fee + payment_fee
        
        return {
            'final_value_fee': final_value_fee,
            'payment_processing_fee': payment_fee,
            'total_fees': total_fees
        }
    
    def calculate_shopify_fees(self, sale_price: float) -> Dict[str, float]:
        """Calculate Shopify fees for a given sale price."""
        transaction_fee = (sale_price * self.SHOPIFY_TRANSACTION_FEE) + self.SHOPIFY_TRANSACTION_FIXED
        
        return {
            'transaction_fee': transaction_fee,
            'total_fees': transaction_fee
        }
    
    def estimate_shipping(self, weight_lbs: float = 2.0) -> float:
        """Estimate shipping cost based on weight."""
        return self.SHIPPING_COST_BASE + (weight_lbs * self.SHIPPING_COST_PER_LB)
    
    def calculate_profit(self, purchase_price: float, sale_price: float, 
                        platform: str = 'ebay', weight_lbs: float = 2.0) -> Dict[str, float]:
        """Calculate profit for a product."""
        # Calculate platform fees
        if platform.lower() == 'ebay':
            fees_breakdown = self.calculate_ebay_fees(sale_price)
            platform_fees = fees_breakdown['total_fees']
        elif platform.lower() == 'shopify':
            fees_breakdown = self.calculate_shopify_fees(sale_price)
            platform_fees = fees_breakdown['total_fees']
        else:
            platform_fees = 0
            fees_breakdown = {'total_fees': 0}
        
        # Estimate shipping
        shipping_cost = self.estimate_shipping(weight_lbs)
        
        # Calculate profit
        total_costs = purchase_price + platform_fees + shipping_cost
        profit = sale_price - total_costs
        profit_margin = (profit / sale_price) if sale_price > 0 else 0
        
        return {
            'purchase_price': purchase_price,
            'sale_price': sale_price,
            'platform_fees': platform_fees,
            'shipping_cost': shipping_cost,
            'total_costs': total_costs,
            'profit': profit,
            'profit_margin': profit_margin,
            'profit_percentage': profit_margin * 100,
            'fees_breakdown': fees_breakdown
        }
    
    def is_profitable(self, purchase_price: float, sale_price: float, 
                     min_margin: float = 0.20, platform: str = 'ebay') -> bool:
        """Check if a product meets minimum profit margin."""
        result = self.calculate_profit(purchase_price, sale_price, platform)
        return result['profit_margin'] >= min_margin
    
    def suggest_listing_price(self, purchase_price: float, target_margin: float = 0.25,
                             platform: str = 'ebay', weight_lbs: float = 2.0) -> float:
        """Suggest a listing price to achieve target margin."""
        # Start with an estimate
        estimated_price = purchase_price * 1.5
        
        # Iterate to find price that gives target margin
        for _ in range(10):  # Max 10 iterations
            result = self.calculate_profit(purchase_price, estimated_price, platform, weight_lbs)
            
            if abs(result['profit_margin'] - target_margin) < 0.01:
                break
            
            # Adjust estimate
            if result['profit_margin'] < target_margin:
                estimated_price *= 1.1
            else:
                estimated_price *= 0.95
        
        return round(estimated_price, 2)
