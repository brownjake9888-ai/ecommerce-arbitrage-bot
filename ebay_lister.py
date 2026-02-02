"""eBay listing automation using eBay SDK."""
import logging
from typing import Dict, Optional
from ebaysdk.trading import Connection as Trading
from config import (
    EBAY_APP_ID, EBAY_DEV_ID, EBAY_CERT_ID, EBAY_AUTH_TOKEN, 
    EBAY_SANDBOX, EBAY_PAYPAL_EMAIL, EBAY_POSTAL_CODE
)

logger = logging.getLogger(__name__)


class EbayLister:
    """Manages eBay listing creation."""
    
    def __init__(self):
        """Initialize eBay API connection."""
        self.api = None
        self.initialized = False
        
        if all([EBAY_APP_ID, EBAY_DEV_ID, EBAY_CERT_ID, EBAY_AUTH_TOKEN]):
            try:
                self.api = Trading(
                    appid=EBAY_APP_ID,
                    devid=EBAY_DEV_ID,
                    certid=EBAY_CERT_ID,
                    token=EBAY_AUTH_TOKEN,
                    config_file=None,
                    domain='api.sandbox.ebay.com' if EBAY_SANDBOX else 'api.ebay.com'
                )
                self.initialized = True
                logger.info("eBay API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize eBay API: {e}")
        else:
            logger.warning("eBay credentials not configured")
    
    def generate_description(self, product_data: Dict) -> str:
        """Generate listing description from product data."""
        title = product_data.get('title', 'Product')
        
        description = f"""
        <div style="font-family: Arial, sans-serif;">
            <h2>{title}</h2>
            <p><strong>Condition:</strong> New</p>
            <p><strong>Fast Shipping:</strong> Ships within 1-2 business days</p>
            <p><strong>Satisfaction Guaranteed:</strong> 30-day returns accepted</p>
            <br>
            <p>Thank you for your business!</p>
        </div>
        """
        return description
    
    def create_listing(self, product_data: Dict, listing_price: float) -> Optional[str]:
        """Create an eBay listing."""
        if not self.initialized:
            logger.error("eBay API not initialized - cannot create listing")
            return None
        
        try:
            title = product_data.get('title', 'Product')[:80]  # eBay title limit
            description = self.generate_description(product_data)
            image_url = product_data.get('image_url', '')
            
            # Prepare listing data
            listing_data = {
                'Item': {
                    'Title': title,
                    'Description': description,
                    'PrimaryCategory': {'CategoryID': '293'},  # General category
                    'StartPrice': listing_price,
                    'CategoryMappingAllowed': 'true',
                    'Country': 'US',
                    'Currency': 'USD',
                    'DispatchTimeMax': '2',
                    'ListingDuration': 'Days_7',
                    'ListingType': 'FixedPriceItem',
                    'PaymentMethods': 'PayPal',
                    'PayPalEmailAddress': EBAY_PAYPAL_EMAIL,
                    'PictureDetails': {
                        'PictureURL': [image_url] if image_url else []
                    },
                    'PostalCode': EBAY_POSTAL_CODE,
                    'Quantity': '1',
                    'ReturnPolicy': {
                        'ReturnsAcceptedOption': 'ReturnsAccepted',
                        'RefundOption': 'MoneyBack',
                        'ReturnsWithinOption': 'Days_30',
                        'ShippingCostPaidByOption': 'Buyer'
                    },
                    'ShippingDetails': {
                        'ShippingType': 'Flat',
                        'ShippingServiceOptions': {
                            'ShippingServicePriority': '1',
                            'ShippingService': 'USPSPriority',
                            'ShippingServiceCost': '5.00'
                        }
                    },
                    'Site': 'US'
                }
            }
            
            # Add item
            response = self.api.execute('AddFixedPriceItem', listing_data)
            
            if response.reply.Ack == 'Success':
                item_id = response.reply.ItemID
                logger.info(f"Successfully created eBay listing: {item_id}")
                return item_id
            else:
                logger.error(f"eBay listing failed: {response.reply}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating eBay listing: {e}")
            return None
    
    def verify_listing(self, item_id: str) -> bool:
        """Verify that a listing was created successfully."""
        if not self.initialized:
            return False
        
        try:
            response = self.api.execute('GetItem', {'ItemID': item_id})
            return response.reply.Ack == 'Success'
        except Exception as e:
            logger.error(f"Error verifying listing: {e}")
            return False
