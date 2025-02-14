FROM python:3.9-slim

WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl

# Expose the port for the app
EXPOSE 5001

# Run the app
CMD ["python", "app.py"]
