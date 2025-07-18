#!/bin/bash
set -e

# Initialize MySQL data directory if empty
if [ ! -d /var/lib/mysql/mysql ]; then
    mysqld --initialize-insecure
fi

# Start MySQL daemon in the background
mysqld_safe --datadir=/var/lib/mysql &

# Wait for MySQL to start
sleep 5

# Create database and user
mysql -u root <<EOSQL
CREATE DATABASE IF NOT EXISTS inventario_uniformes;
CREATE USER IF NOT EXISTS 'inventario_user'@'localhost' IDENTIFIED BY 'Sk1llN3t.2025';
GRANT ALL PRIVILEGES ON inventario_uniformes.* TO 'inventario_user'@'localhost';
FLUSH PRIVILEGES;
EOSQL

# Load schema and initial data
mysql -u root inventario_uniformes < /app/schema.sql

# Run the application
exec python /app/inventario/app_flask_inventario.py
