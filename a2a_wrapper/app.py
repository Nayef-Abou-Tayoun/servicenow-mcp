"""
A2A Wrapper for watsonx.ai Agent
Converts ContextForge A2A protocol to watsonx.ai format
"""

from flask import Flask, request, jsonify
import requests
import os
import logging
import json
import re

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


def parse_sse_response(sse_text):
    """Parse Server-Sent Events response and extract the complete message"""
    try:
        # Extract all content chunks from SSE format
        content_parts = []
        for line in sse_text.split('\n'):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            content_parts.append(delta['content'])
                except json.JSONDecodeError:
                    continue
        
        # Join all content parts
        full_content = ''.join(content_parts)
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', full_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find JSON directly
        json_match = re.search(r'(\{.*\})', full_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # If no JSON found, return the text as-is
        return {"response": full_content}
        
    except Exception as e:
        logger.error(f"Failed to parse SSE response: {e}")
        return {"response": sse_text}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """
    Main chat endpoint for A2A protocol
    Supports both simple format and A2A JSON-RPC format
    """
    # Handle GET requests with usage information
    if request.method == 'GET':
        return jsonify({
            "endpoint": "/chat",
            "method": "POST",
            "description": "Chat endpoint for A2A protocol",
            "usage": {
                "content_type": "application/json",
                "simple_format": {
                    "message": "Your message here"
                },
                "a2a_jsonrpc_format": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "message/send",
                    "params": {
                        "message": {
                            "kind": "message",
                            "role": "user",
                            "parts": [{"kind": "text", "text": "Your message here"}]
                        }
                    }
                }
            },
            "curl_example": 'curl -X POST ' + request.url + ' -H "Content-Type: application/json" -d \'{"message": "Hello"}\''
        }), 200
    
    try:
        logger.info("=== Chat endpoint called ===")
        
        data = request.json
        logger.info(f"Received data: {data}")
        
        if not data:
            logger.error("No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract message from either simple format or A2A JSON-RPC format
        message = None
        
        # Check for A2A JSON-RPC format
        if data.get('jsonrpc') == '2.0' and data.get('method') == 'message/send':
            params = data.get('params', {})
            msg_obj = params.get('message', {})
            parts = msg_obj.get('parts', [])
            if parts and len(parts) > 0:
                message = parts[0].get('text', '')
            logger.info(f"Extracted from A2A JSON-RPC format: {message}")
        
        # Fallback to simple format
        if not message:
            message = data.get('message') or data.get('query') or data.get('content', '')
            logger.info(f"Extracted from simple format: {message}")
        
        if not message:
            logger.error(f"No message found in data: {data}")
            return jsonify({"error": "No message provided"}), 400
        
        logger.info(f"Processing message: {message[:100]}...")
        
        # Check if API key is set
        if not IBM_CLOUD_API_KEY:
            logger.warning("IBM_CLOUD_API_KEY not set - returning demo response")
            return jsonify({
                "response": f"Demo mode: Received your message '{message[:50]}...' but IBM_CLOUD_API_KEY is not configured. Please set the API key to enable full functionality."
            }), 200
        
        # Convert to watsonx format
        watsonx_payload = {
            "messages": [
                {"role": "user", "content": message}
            ]
        }
        
        # Get token and call watsonx
        logger.info("Getting IAM token...")
        token = get_iam_token()
        logger.info("IAM token obtained successfully")
        
        logger.info(f"Calling watsonx endpoint: {WATSONX_ENDPOINT}")
        response = requests.post(
            WATSONX_ENDPOINT,
            json=watsonx_payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=60  # Increased timeout to 60 seconds
        )
        
        logger.info(f"watsonx response status: {response.status_code}")
        
        if response.ok:
            # Parse the SSE streaming response
            parsed_response = parse_sse_response(response.text)
            
            # If it's already a dict with target/payload, return it directly
            if isinstance(parsed_response, dict) and 'target' in parsed_response:
                return jsonify(parsed_response)
            
            # Otherwise wrap it in response field
            return jsonify({
                "response": json.dumps(parsed_response) if isinstance(parsed_response, dict) else str(parsed_response)
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
