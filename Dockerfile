# Multi-stage build for production hardening
# Target: <200MB, non-root user, security best practices

# ============================================
# Stage 1: Builder (Dependencies compilation)
# ============================================
FROM python:3.10-slim AS builder

WORKDIR /build

# Install build dependencies (gcc for numpy compilation)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ============================================
# Stage 2: Runtime (Minimal production image)
# ============================================
FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=false \
    PATH="/home/appuser/.local/bin:$PATH"

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /wheels

# Install dependencies from wheels (no compilation needed)
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy application code (minimal files only)
COPY --chown=appuser:appuser app.py tsp_agent.py ./
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser templates/ ./templates/

# Note: static/ folder empty, so skipped
# Note: data/ created above for runtime persistence

# Expose port
EXPOSE 5000

# Health check (using python -c instead of requests to reduce dependencies)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run application as non-root user
CMD ["python", "app.py"]
