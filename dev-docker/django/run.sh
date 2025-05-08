#!/bin/bash
set -e  # Exit on error

cd /project

echo "Waiting for database to be ready..."

# Wait until PostgreSQL is accepting connections
until pg_isready -h "$DATABASE_HOST" -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for postgres at $DATABASE_HOST:5432..."
  sleep 2
done

echo "Database is up. Running migrations..."
./manage.py migrate

echo "Starting Django development server..."
./manage.py runserver 0.0.0.0:8000
