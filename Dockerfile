FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Run your scheduler
# Use module mode so imports like "from app..." work correctly
CMD ["python", "-m", "app.run_ticker"]
