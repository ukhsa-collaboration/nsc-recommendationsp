#!/bin/sh
set -e
# Start ClamAV daemon in background
echo "Starting ClamAV daemon..."

mkdir -p /var/run/clamav
chown -R 100:100 /var/run/clamav   # change 1000:1000 → 100:100
chmod -R 750 /var/run/clamav       # tighten perms, enough for clamd

echo "✅ Checking clamdscan path..."
which clamdscan || echo "❌ clamdscan not found"


clamd &

# Wait briefly to ensure clamd starts
sleep 2

pgrep -af clamd || echo "❌ clamd is NOT running!"


cd /project

echo "Waiting for database to be ready..."
until pg_isready -h "$DATABASE_HOST" -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for postgres at $DATABASE_HOST:5432..."
  sleep 2
done

echo "Database is up. Running migrations..."
./manage.py migrate

echo "Starting Django development server..."
./manage.py runserver 0.0.0.0:8000
