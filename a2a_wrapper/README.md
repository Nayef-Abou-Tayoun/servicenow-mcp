# watsonx.ai A2A Wrapper

A2A (Agent-to-Agent) protocol wrapper for watsonx.ai agents to enable integration with IBM ContextForge and watsonx Orchestrate.

## Overview

This wrapper converts ContextForge's A2A protocol format to watsonx.ai's native format, enabling seamless agent-to-agent communication.

## Features

- ✅ A2A protocol compatibility
- ✅ Automatic IBM Cloud IAM authentication
- ✅ Health check endpoint
- ✅ Error handling and logging
- ✅ Docker support
- ✅ IBM Cloud Code Engine ready

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
cp .env.example .env
# Edit .env and add your IBM_CLOUD_API_KEY
```

3. **Run the application:**
```bash
python app.py
```

The server will start on `http://localhost:8080`

### Test the Wrapper

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Network issue in area 403"}'
```

## Deployment

### Deploy to IBM Cloud Code Engine

1. **Build and push Docker image:**
```bash
docker build -t us.icr.io/<namespace>/watsonx-a2a-wrapper:latest .
docker push us.icr.io/<namespace>/watsonx-a2a-wrapper:latest
```

2. **Deploy to Code Engine:**
```bash
ibmcloud ce application create \
  --name watsonx-a2a-wrapper \
  --image us.icr.io/<namespace>/watsonx-a2a-wrapper:latest \
  --env IBM_CLOUD_API_KEY=<your-api-key> \
  --env WATSONX_ENDPOINT=<your-watsonx-endpoint> \
  --port 8080 \
  --min-scale 1 \
  --max-scale 5
```

3. **Get the application URL:**
```bash
ibmcloud ce application get --name watsonx-a2a-wrapper
```

### Deploy from GitHub

```bash
ibmcloud ce application create \
  --name watsonx-a2a-wrapper \
  --build-source https://github.com/Nayef-Abou-Tayoun/servicenow-mcp \
  --build-context-dir a2a_wrapper \
  --env IBM_CLOUD_API_KEY=<your-api-key> \
  --env WATSONX_ENDPOINT=<your-watsonx-endpoint> \
  --port 8080
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `IBM_CLOUD_API_KEY` | Yes | IBM Cloud API key for IAM authentication |
| `WATSONX_ENDPOINT` | No | watsonx.ai deployment endpoint (default provided) |
| `PORT` | No | Port to run the server on (default: 8080) |

### Get IBM Cloud API Key

1. Go to https://cloud.ibm.com/iam/apikeys
2. Click "Create"
3. Give it a name (e.g., "watsonx-a2a-wrapper")
4. Copy and save the API key

## API Endpoints

### POST /chat

Main chat endpoint for A2A communication.

**Request:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "response": "Agent response here"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /

API information endpoint.

## Integration with ContextForge

1. **Deploy this wrapper** to IBM Cloud Code Engine
2. **Get the application URL** (e.g., `https://watsonx-a2a-wrapper.xxx.codeengine.appdomain.cloud`)
3. **Add A2A Agent in ContextForge:**
   - Agent Name: `Network_Diagnostic_agent`
   - Endpoint URL: `https://your-wrapper-url/chat`
   - Agent Type: `Custom`
   - Authentication Type: `None` (authentication handled by wrapper)
   - Description: `Network diagnostic agent for incident analysis`

## Troubleshooting

### HTTP 500 Error

- Check that `IBM_CLOUD_API_KEY` is set correctly
- Verify the watsonx endpoint URL is correct
- Check application logs: `ibmcloud ce application logs --name watsonx-a2a-wrapper`

### Authentication Errors

- Ensure your API key has access to the watsonx.ai deployment
- Verify the API key hasn't expired
- Check IAM permissions

### Timeout Errors

- Increase the timeout in Code Engine: `--request-timeout 300`
- Check watsonx.ai deployment status

## Development

### Project Structure

```
a2a_wrapper/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env.example       # Environment variables template
└── README.md          # This file
```

### Adding Features

The wrapper is designed to be simple and extensible. To add features:

1. Modify `app.py` to add new endpoints or logic
2. Update `requirements.txt` if adding dependencies
3. Test locally before deploying
4. Update this README with new features

## License

MIT License - See main repository LICENSE file

## Support

For issues or questions:
- Open an issue in the GitHub repository
- Check IBM Cloud Code Engine documentation
- Review watsonx.ai documentation