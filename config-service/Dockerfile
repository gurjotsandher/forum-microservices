FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl

EXPOSE 5002
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD curl -f http://localhost:5002/ || exit 1

CMD ["python", "app.py"]
