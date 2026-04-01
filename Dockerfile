FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir .

# Default to HTTP transport for remote deployment
ENV PLAUD_TRANSPORT=http
ENV PLAUD_MCP_PORT=8000
ENV PLAUD_MCP_HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "-m", "plaud_notes_mcp.server"]
