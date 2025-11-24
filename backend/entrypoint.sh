#!/bin/bash
set -e

# Создаем директорию для базы данных
mkdir -p /app/data
chmod 777 /app/data

# Создаем файл базы данных через sqlite3
DB_PATH="/app/data/focusflow.db"
if [ ! -f "$DB_PATH" ]; then
    echo "Creating database file: $DB_PATH"
    touch "$DB_PATH"
    chmod 666 "$DB_PATH"
fi

# Запускаем приложение
exec uvicorn main:app --host 0.0.0.0 --port 8000

