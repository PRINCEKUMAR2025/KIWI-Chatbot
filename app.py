import os
import logging
from flask import Flask, request, jsonify, render_template
from chatbot import ECommerceBot

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Initialize the chatbot
try:
    ecommerce_bot = ECommerceBot()
    logger.info("Chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {str(e)}")
    ecommerce_bot = None

@app.route('/')
def index():
    """Render the web interface for testing the chatbot"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot interaction"""
    try:
        # Get the data from the request
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_message = data.get('message')
        user_id = data.get('user_id', None)
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Process the message and get a response from the chatbot
        if ecommerce_bot:
            response = ecommerce_bot.process_query(user_message, user_id)
            return jsonify({"response": response})
        else:
            return jsonify({"error": "Chatbot is not initialized"}), 500
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    """API endpoint to trigger model training (for admin use)"""
    try:
        global ecommerce_bot
        # This could be a protected endpoint with authentication
        if ecommerce_bot:
            ecommerce_bot.train_model()
            return jsonify({"status": "Training completed successfully"})
        else:
            ecommerce_bot = ECommerceBot()
            return jsonify({"status": "Chatbot initialized and training completed"})
    
    except Exception as e:
        logger.error(f"Error in train_model endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred during training: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)