import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, data_path='attached_assets/formatted_dataset.jsonl'):
        """Initialize the data processor with the path to the dataset"""
        self.data_path = data_path
        logger.info(f"Data processor initialized with data path: {data_path}")
        
        # Storage for processed data
        self.products = {}
        self.orders = {}
        self.users = {}
    
    def load_data(self):
        """Load and process the data from the JSONL file"""
        try:
            dataset = []
            with open(self.data_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():  # Skip empty lines
                        dataset.append(json.loads(line))
            
            # Process specific data types
            self._categorize_data(dataset)
            
            logger.info(f"Loaded {len(dataset)} entries from dataset")
            return dataset
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return []
    
    def _categorize_data(self, data):
        """Categorize data into products, orders, and users"""
        for item in data:
            # Check if it's product data
            if 'product details' in item.get('instruction', '').lower():
                # Extract product name from input
                product_name = self._extract_value(item.get('input', ''), 'Product Name:')
                if product_name:
                    self.products[product_name] = {
                        'info': item.get('output', '')
                    }
            
            # Check if it's order data
            elif 'order details' in item.get('instruction', '').lower():
                # Extract order ID from input
                order_id = self._extract_value(item.get('input', ''), 'Order ID:')
                if order_id:
                    self.orders[order_id] = {
                        'info': item.get('output', '')
                    }
            
            # Check if it's user data
            elif 'user profile' in item.get('instruction', '').lower():
                # Extract user ID from input
                user_id = self._extract_value(item.get('input', ''), 'User ID:')
                if user_id:
                    self.users[user_id] = {
                        'info': item.get('output', '')
                    }
    
    def _extract_value(self, text, prefix):
        """Extract a value from text that follows a specific prefix"""
        lines = text.split('\n')
        for line in lines:
            if prefix in line:
                return line.replace(prefix, '').strip()
        return None
    
    def get_product_info(self, product_name):
        """Get information about a specific product"""
        if product_name in self.products:
            return self.products[product_name]['info']
        
        # Try to find a partial match
        for name, info in self.products.items():
            if product_name.lower() in name.lower():
                return info['info']
        
        return "Product not found in our database."
    
    def get_user_info(self, user_id):
        """Get information about a specific user"""
        if user_id in self.users:
            return self.users[user_id]['info']
        return "User not found in our database."
    
    def get_order_info(self, order_id=None, product_name=None):
        """Get information about orders, filtered by order_id or product_name if provided"""
        if order_id and order_id in self.orders:
            return self.orders[order_id]['info']
        
        if product_name:
            # Return orders that contain this product (not implemented in this simple version)
            pass
        
        return "Order not found in our database."
