#!/usr/bin/env bash
set -e
pip install -r requirements.txt
# Збираємо статику ДО старту
python manage.py collectstatic --noinput
# Мінімальні міграції для Django службових таблиць (SQLite-файл, не in-memory)
python manage.py migrate --noinput
