FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app:/app/common

WORKDIR /app

# Install core dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install debugpy for debugging
RUN pip install debugpy==1.6.7

# Copy the rest of the application code
COPY . .

# Expose both Flask and debugpy ports
EXPOSE 5000 5678  

CMD ["python", "app.py"]