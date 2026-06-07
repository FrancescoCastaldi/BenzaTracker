FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for matplotlib
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and install the package
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

# Volume for persistent data (SQLite database)
VOLUME /app/data

# Default: run web interface
ENV DATA_DIR=/app/data
EXPOSE 5000

CMD ["python", "-m", "benzatracker.web"]
