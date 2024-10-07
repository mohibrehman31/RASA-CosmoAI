from flask import Flask, request, jsonify
import requests
import os
import logging
from requests.exceptions import RequestException

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use environment variable for Rasa URL, with a default fallback
RASA_API_URL = os.environ.get('RASA_API_URL', 'http://127.0.0.1:5005/webhooks/rest/webhook')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Send the message to Rasa
        try:
            rasa_response = requests.post(RASA_API_URL, json={"sender": "user", "message": user_message}, timeout=5)
            rasa_response.raise_for_status()  # Raises an HTTPError for bad responses
        except RequestException as e:
            logger.error(f"Error communicating with Rasa: {str(e)}")
            return jsonify({"error": "Unable to communicate with the chatbot service"}), 503

        # Extract the text from Rasa's response
        response_text = [msg.get('text', '') for msg in rasa_response.json()]
        
        return jsonify({"response": response_text})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # You might want to add more sophisticated health checks here
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)