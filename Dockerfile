FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
COPY config/ ./config/

# Install the package in development mode
RUN pip install -e .

EXPOSE 8080

CMD ["servicenow-mcp-sse", "--host=0.0.0.0", "--port=8080"]
