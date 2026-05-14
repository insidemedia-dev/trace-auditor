FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the actual application code
COPY src/ ./src/

# Run the auditor as a non-root user for K8s security best practices
RUN useradd -m auditor
USER auditor

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "trace_auditor"]
