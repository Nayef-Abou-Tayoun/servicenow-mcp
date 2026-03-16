"""
A2A Wrapper for watsonx.ai Agent
Converts ContextForge A2A protocol to watsonx.ai format
"""

from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
WATSONX_ENDPOINT = os.getenv(
    "WATSONX_ENDPOINT",
    "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/718c2fec-317e-4bd5-bcea-122b4e97ce70/ai_service_stream?version=2021-05-01"
)
IBM_CLOUD_API_KEY = os.getenv("IBM_CLOUD_API_KEY")

if not IBM_CLOUD_API_KEY:
    logger.warning("IBM_CLOUD_API_KEY not set - authentication will fail")


def get_iam_token():
    """Get IBM Cloud IAM token from API key"""
    try:
        response = requests.post(
            'https://iam.cloud.ibm.com/identity/token',
            data={
                "apikey": IBM_CLOUD_API_KEY,
                "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Failed to get IAM token: {e}")
        raise


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for A2A protocol
    Accepts: {"message": "user message"} or {"query": "user message"}
    Returns: {"response": "agent response"}
    """
    try:
        # Get message from ContextForge A2A format
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        message = data.get('message') or data.get('query') or data.get('content', '')
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        logger.info(f"Received message: {message[:100]}...")
        
        # Convert to watsonx format
        watsonx_payload = {
            "messages": [
                {"role": "user", "content": message}
            ]
        }
        
        # Get token and call watsonx
        token = get_iam_token()
        
        logger.info(f"Calling watsonx endpoint: {WATSONX_ENDPOINT}")
        response = requests.post(
            WATSONX_ENDPOINT,
            json=watsonx_payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        logger.info(f"watsonx response status: {response.status_code}")
        
        if response.ok:
            # Try to parse JSON response
            try:
                watsonx_response = response.json()
                # Extract the actual response text
                response_text = watsonx_response.get('results', [{}])[0].get('generated_text', str(watsonx_response))
            except:
                response_text = response.text
            
            return jsonify({
                "response": response_text
            })
        else:
            logger.error(f"watsonx error: {response.status_code} - {response.text}")
            return jsonify({
                "error": f"watsonx error: {response.status_code}",
                "details": response.text
            }), 500
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info"""
    return jsonify({
        "name": "watsonx A2A Wrapper",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/chat": "Chat endpoint (POST with {message: 'text'})"
        }
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

# Made with Bob
