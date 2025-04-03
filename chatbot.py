import os
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from data_processor import DataProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    # Create the directory for NLTK data
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    # Set the NLTK data path
    nltk.data.path.append(nltk_data_dir)
    
    # Download the necessary resources
    nltk.download('punkt', download_dir=nltk_data_dir)
    nltk.download('stopwords', download_dir=nltk_data_dir)
    logger.info("NLTK data downloaded successfully")
except Exception as e:
    logger.error(f"Failed to download NLTK data: {str(e)}")

class ECommerceBot:
    def __init__(self, data_source=None, drive_url=None):
        """Initialize the e-commerce chatbot with either local file path or Google Drive URL"""
        self.data_processor = DataProcessor(data_source=data_source, drive_url=drive_url)
        self.dataset = self.data_processor.load_data()
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.preprocess_text,
            stop_words='english'  # Use built-in English stopwords
        )
        
        # Prepare the model
        self.prepare_model()
        logger.info("E-commerce chatbot initialized")
    
    def prepare_model(self):
        """Prepare the model by vectorizing the training data"""
        if not self.dataset:
            logger.error("No dataset available for model preparation")
            return
        
        # Extract instructions and inputs for vectorization
        corpus = []
        for item in self.dataset:
            corpus.append(f"{item['instruction']} {item['input']}")
        
        # Fit the vectorizer on the corpus
        self.X = self.vectorizer.fit_transform(corpus)
        logger.info(f"Model prepared with {len(corpus)} training examples")
    
    def preprocess_text(self, text):
        """Preprocess the text by tokenizing and removing stopwords"""
        try:
            # Convert to lowercase and tokenize
            # Use a simple split to avoid NLTK tokenization issues in this environment
            tokens = text.lower().split()
            # Remove punctuation and non-alphabetic tokens
            tokens = [token for token in tokens if token.isalpha()]
            return tokens
        except Exception as e:
            logger.error(f"Error in text preprocessing: {str(e)}")
            return []
    
    def find_most_similar(self, query):
        """Find the most similar training example to the user query"""
        try:
            # Vectorize the query
            query_vec = self.vectorizer.transform([query])
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(query_vec, self.X).flatten()
            
            # Find the index of the most similar example
            best_match_idx = np.argmax(similarity_scores)
            similarity_score = similarity_scores[best_match_idx]
            
            # Return the best match if similarity is above threshold
            if similarity_score > 0.3:  # Adjustable threshold
                return self.dataset[best_match_idx], similarity_score
            else:
                return None, similarity_score
        except Exception as e:
            logger.error(f"Error finding similar query: {str(e)}")
            return None, 0
    
    def process_query(self, query, user_id=None):
        """Process a user query and return an appropriate response"""
        try:
            # Determine the intent of the query
            intent = self.determine_intent(query)
            
            # Find the most similar training example
            best_match, score = self.find_most_similar(query)
            
            if not best_match:
                return "I'm sorry, I don't understand your query. Could you please be more specific about product, order, or account information?"
            
            # Generate response based on the best match
            if 'output' in best_match:
                # If user_id is provided and the query is about user info
                if user_id and ('check user' in best_match['instruction'].lower() or 'retrieve user' in best_match['instruction'].lower()):
                    # Replace the example user ID with the provided one
                    modified_input = f"User ID: {user_id}"
                    
                    # Find a new match with the modified input
                    for item in self.dataset:
                        if item['instruction'] == best_match['instruction'] and 'User ID:' in item['input']:
                            query_vec = self.vectorizer.transform([f"{item['instruction']} {modified_input}"])
                            return item['output']
                    
                    return best_match['output']
                else:
                    return best_match['output']
            else:
                return "I found something similar, but I'm not sure how to respond. Please try rephrasing your question."
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "Sorry, an error occurred while processing your request. Please try again later."
    
    def determine_intent(self, query):
        """Determine the intent of the user query"""
        query_lower = query.lower()
        
        # Check for different intents based on keywords
        if any(word in query_lower for word in ['order', 'buy', 'purchase', 'delivery']):
            return 'order_info'
        elif any(word in query_lower for word in ['product', 'item', 'price', 'cost']):
            return 'product_info'
        elif any(word in query_lower for word in ['account', 'profile', 'login', 'sign']):
            return 'account_info'
        elif any(word in query_lower for word in ['address', 'shipping', 'location']):
            return 'address_info'
        elif any(word in query_lower for word in ['coin', 'balance', 'credit']):
            return 'balance_info'
        else:
            return 'general'
    
    def train_model(self):
        """Retrain the model with updated data"""
        # Reload data in case it has changed
        self.dataset = self.data_processor.load_data()
        self.prepare_model()
        logger.info("Model retrained successfully")
