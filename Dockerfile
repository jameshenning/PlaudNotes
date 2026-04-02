FROM python:3.12-slim

WORKDIR /app

# Install build tools needed for native extensions (cryptography, pydantic-core)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir .

# Clean up build tools to reduce image size
RUN apt-get purge -y --auto-remove gcc python3-dev

# Create non-root user and set ownership
RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /sbin/nologin mcp && \
    chown -R mcp:mcp /app

USER mcp

ENV PLAUD_TRANSPORT=http
ENV PLAUD_MCP_PORT=8000
ENV PLAUD_MCP_HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "-m", "plaud_notes_mcp.server"]
