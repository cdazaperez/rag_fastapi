FROM python:3.11-slim

# Install MySQL server
RUN apt-get update \
    && apt-get install -y mysql-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8082
CMD ["/entrypoint.sh"]
