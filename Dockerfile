FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies for any native extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir --prefix=/install .

# --- Runtime stage (slim, no build tools) ---
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /sbin/nologin mcp

# Copy installed packages from builder
COPY --from=builder /install /usr/local
COPY --from=builder /app /app
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Default to HTTP transport for remote deployment
ENV PLAUD_TRANSPORT=http
ENV PLAUD_MCP_PORT=8000
ENV PLAUD_MCP_HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "-m", "plaud_notes_mcp.server"]
